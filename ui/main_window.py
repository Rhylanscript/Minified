# ui/main_window.py

"""
Main application window for the Minified GUI.

This module defines the primary user interface, including:
- file selection and drop & drag support
- asynchronous file minification
- export functionality for processed files
- logging system with coloured output
- theme switching (light/dark mode)
- progress tracking during processing

The window acts as a central controller which connects the
GUI to the backend.
"""

import os
import subprocess
import sys

from typing import override

from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLabel

from core.file_manager import FileManager
from core.task_manager import TaskManager
from core.export_manager import ExportManager

from ui.toast import Toast
from ui.widgets.log_view import LogView
from ui.widgets.progress_widget import ProgressWidget
from ui.widgets.theme_toggle import ThemeToggle

class MainWindow(QWidget):
    """
    Main application window for the Minified tool.

    Provides a full graphical user interface for selecting files,
    running minification tasks, viewing logs and exporting results.

    Key roles:
    - Managing selected input files
    - Launching background minification workers on threads
    - Displaying progress and minification updates
    - Handling export of processed files
    - Managing theme switching (light/dark)
    - Providing user feedback via logs and toasts

    This class acts as the central UI controller of the application.
    """
    def __init__(self, initial_theme: str = "light") -> None:
        """
        Initialisation of the main window and builds the UI.

        Sets up:
        - Sidebar with action buttons and theme button
        - Output log viewer
        - Progress bar system
        - Drag and drop file support

        Args:
            initial_theme: Starting UI theme (light or dark)

        Side Effects:
        - Builds and configures full UI layout
        - Connects all button signals
        - Initialises logging system
        """
        super().__init__()
        self._configure_window()

        # call init functions
        self._init_state()
        self._build_widgets(initial_theme)
        self._build_layouts()
        self._connect_signals()
        self._apply_defaults()

        # log initialisation
        self.output.info("Minified Initialised")

        # test log funcs
        # self.output.warn("This is a Warning")
        # self.output.error("This is an Error")
        # self.output.success("This is a Success")

    # --------- INITIALISATION FUNCTIONS ---------

    def _configure_window(self) -> None:
        """Configure application window properties."""
        self.setWindowTitle("Minified")
        self.resize(800, 500)

        # allow dropping of files onto the app
        self.setAcceptDrops(True)

    def _init_state(self) -> None:
        """Initialise class attributes."""
        self.minified_results: list[tuple[str, str]] = []

        self.file_manager = FileManager()
        self.task_manager = TaskManager()
        self.export_manager = ExportManager()

    def _build_widgets(self, initial_theme: str) -> None:
        """Create application widgets."""
        # --- action buttons
        self.open_btn = QPushButton("Open File")
        self.minify_btn = QPushButton("Minify")
        self.export_btn = QPushButton("Export")
        self.clear_btn = QPushButton("Clear Logs")
        
        # --- theme toggle
        self.theme_toggle = ThemeToggle(initial_theme)
        
        # --- file label
        self.file_label = QLabel("No file selected")
        
        # --- progress bar
        self.progress = ProgressWidget()

        # --- output log
        self.output = LogView()

    def _build_layouts(self) -> None:
        """Create and add objects to layouts."""
        # make layouts
        main_layout = QHBoxLayout()

        sidebar = QVBoxLayout()
        content = QVBoxLayout()

        # add to sidebar
        sidebar.addWidget(self.open_btn)
        sidebar.addWidget(self.minify_btn)
        sidebar.addWidget(self.export_btn)
        sidebar.addWidget(self.clear_btn)
        sidebar.addStretch()
        sidebar.addWidget(self.theme_toggle)

        # add to main content
        content.addWidget(self.file_label)
        content.addWidget(self.progress)
        content.addWidget(self.output)
        
        # setup widget objects for panels
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(sidebar)

        # set layout
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addLayout(content, 4)

        # set layout of application
        self.setLayout(main_layout)

    def _connect_signals(self) -> None:
        """Connect signals of helper methods to objects."""
        # --- connect button actions
        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.export_btn.clicked.connect(self.export_file)
        self.clear_btn.clicked.connect(self.output.clear_logs)

        # connect log link clicks
        self.output.anchorClicked.connect(self.handle_link_click)

        # connect file manager update
        self.file_manager.on_change = self.on_files_changed

    def _apply_defaults(self) -> None:
        """Applies the default states to objects and other stuff."""
        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

    # --------- BUTTON FUNCTIONS ----------

    def open_file(self) -> None:
        """
        Opens a file selection dialogue and stores selected file paths.

        Updates the UI with selected filenames and enables the minify
        button if valid files are selected.
        """
        files, _ = QFileDialog.getOpenFileNames(self)
        self.file_manager.set_files(files)

    def run_minify(self) -> None:
        """
        Starts the asynchronous minification process.

        Creates a QThread and MinifyWorker to process selected files
        without blocking UI through TaskManager.

        Connects worker signals to UI handlers for:
        - progress updates
        - logging output
        - completion handling
        """

        if not self.file_manager.has_files(): 
            self.output.warn("No target files specified")
            self.export_btn.setEnabled(False)
            return
        
        if self.task_manager.is_busy():
            self.output.warn("Minification already in progress.")
            return
        
        # disable buttons during processing and reset pgb
        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.progress.show_progress()
        self.progress.set_progress(0)

        self.output.info("Starting minification...")

        # create thread + worker
        worker = self.task_manager.start_minify(self.file_manager.get_files())

        # connect signals
        worker.finished.connect(self.on_minify_finished)
        worker.progress.connect(self.progress.set_progress)

        worker.log.connect(self.output.log)
        worker.error.connect(self.output.error)
        worker.warn.connect(self.output.warn)
        worker.success.connect(self.output.success)
        worker.info.connect(self.output.info)

    def export_file(self) -> None:
        """
        Exports minified results to a selected location using 
        ExportManager.

        If a single file was processed, prompts for a save location.
        If multiple files processed, prompts for a folder.

        Writes minified content to files and displays confirmation or
        error messages in the log.
        """
        if not self.minified_results:
            self.output.warn("Nothing to export")
            return
        
        try:
            export_dir = self.export_manager.export_files(self, self.minified_results, self.output)
            if not export_dir: return

            self.show_export_toast()

        except Exception as e:
            self.output.error(f"Export failed: {str(e)}")

    def on_minify_finished(self, results: list[tuple[str, str]]) -> None:
        """
        Handles completion of the minification process.

        Stores results, updates UI, re-enables controls, and 
        transitions progress UI back into idle state.

        Args:
            results: A list of the minified files in format of `[(path, content), ...]`
        """
        self.minified_results = results

        self.output.info("Minification complete")

        self.minify_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        self.progress.set_progress(100)
        QTimer.singleShot(800, self.progress.show_idle)

    def open_output_folder(self) -> None:
        """
        Method to open the folder that files were just exported to.

        Uses `subprocess` or `os` modules to open file explorer 
        depending on operating system.
        """
        if not self.export_manager.last_export_dir:
            self.output.warn("No export folder available")
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(self.export_manager.last_export_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.export_manager.last_export_dir])
            else:
                subprocess.Popen(["xdg-open", self.export_manager.last_export_dir])

            self.output.info("Opened output folder")

        except Exception as e:
            self.output.error(f"Failed to open folder: {str(e)}")

    # -------- HELPER FUNCTIONS ------------

    def on_files_changed(self, files: list[str]) -> None:
        """
        Helper method called when files in filemanager are changed.

        Updates label and logs changes to output.

        Args:
            files: A list of the files being added
        """
        self.file_label.setText(f"{len(files)} file(s) selected")

        if files:
            self.output.info("Files selected:")
            for name in self.file_manager.get_names():
                self.output.log(f"  - {name}", log_time=False)

            self.minify_btn.setEnabled(True)
        else:
            self.output.warn("No target files selected")
            self.file_label.setText("No files selected")
            self.minify_btn.setEnabled(False)

    def handle_link_click(self, url: str) -> None:
        """
        Helper method to open a url when a file link is clicked in logs.

        Takes a url and uses the same logic as before to open file 
        explorer, while handling potential errors.

        Args:
            url: The url of the folder to open

        I havent actually tried this on other machines but it works on
        my machine so oh well :)
        """
        path = url.toLocalFile()

        if not path: path = url.toString().replace("open://", "")

        try:
            if sys.platform == "win32":
                subprocess.Popen([f'explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(path)])
        
        except Exception as e:
            self.output.error(f"Failed to open file location: {str(e)}")

    def show_export_toast(self) -> None:
        """
        Method to show export toast when file/files are exported.
        Uses the `Toast` class to show a little popup.

        When clicked, opens last export directory.
        """
        if not self.export_manager.last_export_dir: return
        toast = Toast(self, "Open Output Folder")

        toast._on_click = self.open_output_folder
        toast.show_toast(self)

    # -------- OVERRIDES ---------

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """
        Function that is called whenever a file is dragged onto the application.
        
        Simply accepts the action provided it has a valid file. Overrides from
        the method of the parent class QWidget.

        Args:
            event: The drag enter event instance.
        """
        if event.mimeData() and event.mimeData().hasUrls(): event.acceptProposedAction()

    @override
    def dropEvent(self, event: QDropEvent) -> None:
        """
        Function that is called whenever a file is dropped onto the application.
        
        Sets the currently selected file to the one that was just dropped.
        Overrides from the method of the parent class QWidget.

        Args:
            event: The drop event instance.
        """
        if not event.mimeData(): return

        # store urls in a list and update files
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.file_manager.set_files(files)