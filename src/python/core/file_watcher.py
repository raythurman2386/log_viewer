import os
from typing import Dict, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.python.utils.logger import setup_logger

logger = setup_logger(__name__)


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory:
            logger.debug(f"File created: {event.src_path}")
            self.callback("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            logger.debug(f"File modified: {event.src_path}")
            self.callback("modified", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            logger.debug(f"File deleted: {event.src_path}")
            self.callback("deleted", event.src_path)


class FileWatcher:
    def __init__(self):
        self.observer = Observer()
        self.observer.start()
        self.handlers: Dict[str, FileEventHandler] = {}

    def watch_directory(self, directory: str, callback: Callable[[str, str], None]) -> None:
        """Watch a directory for file changes.

        Args:
            directory: Directory path to watch
            callback: Function to call when changes occur, receives (event_type, file_path)
        """
        try:
            handler = FileEventHandler(callback)
            self.observer.schedule(handler, directory, recursive=False)
            self.handlers[directory] = handler
            logger.info(f"Started watching directory: {directory}")
        except Exception as e:
            logger.error(f"Error setting up directory watch for {directory}: {e}")
            raise

    def watch_file(self, file_path: str, callback: Callable[[str, str], None]) -> None:
        """Watch a specific file for changes.

        Args:
            file_path: Path to the file to watch
            callback: Function to call when changes occur, receives (event_type, file_path)
        """
        try:
            directory = os.path.dirname(file_path)
            if file_path not in self.handlers:
                handler = FileEventHandler(
                    lambda event_type, path: (
                        callback(event_type, path) if path == file_path else None
                    )
                )
                self.observer.schedule(handler, directory, recursive=False)
                self.handlers[file_path] = handler
                logger.info(f"Started watching file: {file_path}")
        except Exception as e:
            logger.error(f"Error setting up file watch for {file_path}: {e}")
            raise

    def stop_watching(self, path: str) -> None:
        """Stop watching a file or directory.

        Args:
            path: Path to stop watching
        """
        try:
            if path in self.handlers:
                handler = self.handlers.pop(path)
                self.observer.unschedule(handler)
                logger.info(f"Stopped watching: {path}")
        except Exception as e:
            logger.error(f"Error stopping watch for {path}: {e}")
            raise

    def stop(self) -> None:
        """Stop all file watching."""
        try:
            self.observer.stop()
            self.observer.join()
            self.handlers.clear()
            logger.info("Stopped all file watching")
        except Exception as e:
            logger.error(f"Error stopping file watcher: {e}")
            raise
