import os
import mmap
from pathlib import Path
from typing import List
from datetime import datetime
import sys
from src.python.utils.logger import setup_logger
from src.python.utils.memory_helpers import log_memory_usage

logger = setup_logger(__name__)

# Try to import C++ module
try:
    build_dir = Path(__file__).resolve().parent.parent.parent.parent / "build" / "Release"
    sys.path.append(str(build_dir))
    import logviewer_cpp

    USING_CPP = True
except ImportError as e:
    logger.warning(f"Could not load C++ module, falling back to Python: {e}")
    USING_CPP = False


class PythonFileLoader:
    """Pure Python implementation of the file loader."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path).resolve()
        self._line_positions: List[int] = []
        self._last_modified: float = 0
        self._total_lines: int = 0
        self._file_size: int = 0
        self._cache_line_positions()

    def _cache_line_positions(self) -> None:
        """Cache the positions of all line beginnings for fast random access."""
        log_memory_usage("Before caching line positions")
        self._line_positions = [0]  # First line starts at position 0
        self._total_lines = 0

        try:
            file_stat = self.file_path.stat()
            self._file_size = file_stat.st_size
            self._last_modified = file_stat.st_mtime

            if self._file_size == 0:
                return  # Empty file

            with self.file_path.open("rb") as f:
                # Normalize line endings for cross-platform consistency
                content = f.read().replace(b"\r\n", b"\n")

                # Memory-map large files (Windows requires special handling)
                if self._file_size >= 1024 * 1024:
                    try:
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            self._cache_from_content(mm[:].replace(b"\r\n", b"\n"))
                            log_memory_usage("After memory mapping large file")
                    except ValueError:
                        logger.warning(
                            f"Memory mapping failed for {self.file_path}, using fallback"
                        )
                        self._cache_from_content(content)
                else:
                    self._cache_from_content(content)

            # If file doesn't end with newline, count the last line
            if self._file_size > 0 and (
                not self._line_positions or self._line_positions[-1] < self._file_size
            ):
                self._total_lines += 1

        except (OSError, IOError) as e:
            logger.error(f"Error reading file {self.file_path}: {e}")
            raise

    def _cache_from_content(self, content: bytes) -> None:
        """Cache line positions from file content."""
        pos = 0
        while pos < len(content):
            next_pos = content.find(b"\n", pos)
            if next_pos == -1:
                break
            self._line_positions.append(next_pos + 1)
            pos = next_pos + 1
            self._total_lines += 1

    def read_lines(self, start: int, count: int) -> List[str]:
        """Read a specific number of lines from the file."""
        if start < 0 or start >= self._total_lines:
            return []

        end = min(start + count, self._total_lines)
        lines = []

        try:
            with self.file_path.open("r", encoding="utf-8", errors="replace") as f:
                for i in range(start, end):
                    f.seek(self._line_positions[i])
                    if i + 1 < len(self._line_positions):
                        line_length = self._line_positions[i + 1] - self._line_positions[i]
                        line = f.read(line_length)
                    else:
                        line = f.readline()
                    lines.append(line.rstrip("\n"))
        except (OSError, IOError) as e:
            logger.error(f"Error reading lines from {self.file_path}: {e}")
            return []

        return lines

    def get_line_count(self) -> int:
        """Get the total number of lines in the file."""
        return self._total_lines

    def has_changed(self) -> bool:
        """Check if the file has been modified."""
        try:
            current_mtime = self.file_path.stat().st_mtime
            return current_mtime > self._last_modified
        except OSError:
            return False

    def reload(self) -> None:
        """Reload the file content if changed."""
        if self.has_changed():
            self._cache_line_positions()

    def get_file_size(self) -> int:
        """Get the size of the file in bytes."""
        return self._file_size

    def get_last_modified(self) -> str:
        """Get the last modification time of the file."""
        return datetime.fromtimestamp(self._last_modified).strftime("%Y-%m-%d %H:%M:%S")


class FileLoader:
    """Main file loader that uses C++ implementation when available."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path).resolve()
        try:
            if USING_CPP:
                self._impl = logviewer_cpp.FileLoader(str(self.file_path))
            else:
                raise ImportError("C++ implementation not available")
        except Exception as e:
            logger.info(f"Using Python implementation: {e}")
            self._impl = PythonFileLoader(self.file_path)

    def read_lines(self, start: int, count: int) -> List[str]:
        return self._impl.read_lines(start, count)

    def get_line_count(self) -> int:
        return self._impl.get_line_count()

    def has_changed(self) -> bool:
        return self._impl.has_changed()

    def reload(self) -> None:
        self._impl.reload()

    def get_file_size(self) -> int:
        return self._impl.get_file_size()

    def get_last_modified(self) -> str:
        return self._impl.get_last_modified()
