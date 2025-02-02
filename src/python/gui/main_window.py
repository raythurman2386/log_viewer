from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QAction, QTextDocument, QFont
import os
from typing import Set, Dict
from core.file_loader import FileLoader
from core.file_watcher import FileWatcher
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileLoaderThread(QThread):
    """Thread for loading files without blocking the GUI."""

    file_loaded = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str, str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            loader = FileLoader(self.file_path)
            content = "\n".join(loader.read_lines(0, loader.get_line_count()))
            self.file_loaded.emit(self.file_path, content)
        except Exception as e:
            logger.error(f"Error loading file {self.file_path}: {e}")
            self.error_occurred.emit(self.file_path, str(e))


class LogViewWidget(QTextEdit):
    """Widget for displaying log content."""

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        self.setReadOnly(True)
        self.loader = FileLoader(file_path)
        font = QFont("Consolas", 10)
        self.setFont(font)
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.setDocument(QTextDocument(self))
        self.load_content()

    def load_content(self):
        try:
            content = "\n".join(self.loader.read_lines(0, self.loader.get_line_count()))
            self.setPlainText(content)
        except Exception as e:
            logger.error(f"Error loading content for {self.file_path}: {e}")
            self.setPlainText(f"Error loading file: {e}")

    def refresh(self):
        """Refresh the content if the file has changed."""
        if self.loader.has_changed():
            logger.debug(f"Refreshing content for {self.file_path}")
            self.loader.reload()
            current_scroll = self.verticalScrollBar().value()
            self.load_content()
            # Restore scroll position
            self.verticalScrollBar().setValue(current_scroll)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Log Viewer")
        self.resize(1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget for multiple log files
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget)

        # Initialize file watcher
        self.file_watcher = FileWatcher()

        # Setup refresh timer for file changes
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.check_file_changes)
        self.refresh_timer.start(1000)  # Check every second

        # Keep track of monitored directories and loading threads
        self.monitored_directories: Set[str] = set()
        self.loading_threads: Dict[str, FileLoaderThread] = {}

        self.setup_ui()

    def setup_ui(self):
        """Initialize the UI components"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        # Actions
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        open_dir_action = QAction("Open Directory", self)
        open_dir_action.triggered.connect(self.open_directory_dialog)
        file_menu.addAction(open_dir_action)

    def open_file_dialog(self):
        """Open file dialog and load selected file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Log File", "", "Log Files (*.log *.txt);;All Files (*.*)"
        )
        if file_path:
            self.add_log_view(file_path)

    def open_directory_dialog(self):
        """Open directory dialog and load all log files"""
        directory = QFileDialog.getExistingDirectory(
            self, "Open Directory", "", QFileDialog.Option.ShowDirsOnly
        )
        if directory:
            self.monitor_directory(directory)

    def monitor_directory(self, directory: str):
        """Monitor a directory for log files and load them"""
        try:
            # Add to monitored directories set
            self.monitored_directories.add(directory)
            logger.info(f"Started monitoring directory: {directory}")

            # First, load existing log files
            for filename in os.listdir(directory):
                if self._is_log_file(filename):
                    full_path = os.path.join(directory, filename)
                    self.add_log_view(full_path)

            # Set up directory monitoring
            self.file_watcher.watch_directory(directory, self._handle_directory_change)

        except Exception as e:
            logger.error(f"Error monitoring directory {directory}: {e}")
            self.monitored_directories.discard(directory)
            QMessageBox.critical(self, "Error", f"Error monitoring directory: {str(e)}")

    def _is_log_file(self, filename: str) -> bool:
        """Check if a file is a log file based on extension"""
        return filename.lower().endswith((".log", ".txt"))

    def _handle_directory_change(self, event_type: str, event_path: str):
        """Handle changes in monitored directory"""
        logger.debug(f"File system event: {event_type} - {event_path}")
        if event_type == "created" and self._is_log_file(event_path):
            # If it's a new log file, add it to the viewer
            self.add_log_view(event_path)
        elif event_type == "modified":
            # Find and refresh the tab if it's open
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if widget.file_path == event_path:
                    widget.refresh()
                    break
        elif event_type == "deleted":
            # Find and close the tab if it's open
            for i in range(self.tab_widget.count()):
                widget = self.tab_widget.widget(i)
                if widget.file_path == event_path:
                    self.close_tab(i)
                    break

    def close_tab(self, index):
        """Close the specified tab"""
        try:
            widget = self.tab_widget.widget(index)
            if widget:
                # Get the file path before removing the tab
                file_path = widget.file_path
                logger.debug(f"Closing tab for {file_path}")

                # Remove the tab first
                self.tab_widget.removeTab(index)

                # Then stop watching the file
                self.file_watcher.stop_watching(file_path)

                # Clean up the widget
                widget.deleteLater()

                # Clean up any loading thread
                if file_path in self.loading_threads:
                    thread = self.loading_threads.pop(file_path)
                    thread.quit()
                    thread.wait()
        except Exception as e:
            logger.error(f"Error closing tab: {e}")

    @pyqtSlot(str, str)
    def _handle_file_loaded(self, file_path: str, content: str):
        """Handle when a file is loaded in the background thread"""
        logger.debug(f"File loaded successfully: {file_path}")
        # Create new tab with content
        tab = LogViewWidget(file_path)
        tab.setPlainText(content)
        self.tab_widget.addTab(tab, os.path.basename(file_path))

        # Clean up the thread
        if file_path in self.loading_threads:
            thread = self.loading_threads.pop(file_path)
            thread.quit()
            thread.wait()

    @pyqtSlot(str, str)
    def _handle_load_error(self, file_path: str, error: str):
        """Handle file loading errors"""
        logger.error(f"Error loading {file_path}: {error}")
        QMessageBox.critical(self, "Error", f"Error loading {file_path}: {error}")

        # Clean up the thread
        if file_path in self.loading_threads:
            thread = self.loading_threads.pop(file_path)
            thread.quit()
            thread.wait()

    def add_log_view(self, file_path: str):
        """Add a new tab with log content"""
        logger.info(f"Adding log view for {file_path}")
        # Check if file is already open
        for i in range(self.tab_widget.count()):
            if self.tab_widget.widget(i).file_path == file_path:
                self.tab_widget.setCurrentIndex(i)
                return

        # Create and start loading thread
        thread = FileLoaderThread(file_path)
        thread.file_loaded.connect(self._handle_file_loaded)
        thread.error_occurred.connect(self._handle_load_error)
        self.loading_threads[file_path] = thread
        thread.start()

    def check_file_changes(self):
        """Check for changes in open files"""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if isinstance(widget, LogViewWidget):
                widget.refresh()

    def closeEvent(self, event):
        """Handle application shutdown"""
        try:
            # Stop the refresh timer
            self.refresh_timer.stop()

            # Stop all file watching
            self.file_watcher.stop()
            logger.info("Stopped file watcher")

            # Clear monitored directories
            self.monitored_directories.clear()

            # Clean up loading threads
            for thread in self.loading_threads.values():
                thread.quit()
                thread.wait()
            self.loading_threads.clear()

            # Accept the close event
            event.accept()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            event.accept()
