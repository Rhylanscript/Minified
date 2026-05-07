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
from PyQt6.QtCore import QThread, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QHBoxLayout, QLabel

from core.worker import MinifyWorker
from utils.util import get_filename
from utils.style_loader import load_stylesheet

from ui.toast import Toast
from ui.widgets.log_view import LogView
from ui.widgets.progress_widget import ProgressWidget

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
        self._init_state(initial_theme)
        self._build_widgets()
        self._build_layouts()
        self._connect_signals()
        self._apply_defaults()

        # log initialisation
        self.output.info("Minified Initialised")

        # test log funcs
        self.output.warn("This is a Warning")
        self.output.error("This is an Error")
        self.output.success("This is a Success")

    # --------- INITIALISATION FUNCTIONS ---------

    def _configure_window(self) -> None:
        self.setWindowTitle("Minified")
        self.resize(800, 500)

        # allow dropping of files onto the app
        self.setAcceptDrops(True)

    def _init_state(self, theme) -> None:
        self.file_paths: list[str] = []
        self.last_results: list[tuple[str, str]] = []
        self.last_export_dir: str | None = None

        self.current_theme = theme

    def _build_widgets(self) -> None:
        # --- action buttons
        self.open_btn = QPushButton("Open File")
        self.minify_btn = QPushButton("Minify")
        self.export_btn = QPushButton("Export")
        self.clear_btn = QPushButton("Clear Logs")
        
        # --- theme toggle
        self.theme_toggle = QPushButton("Light Mode" if self.current_theme == "dark" else "Dark Mode")
        self.theme_toggle.setCheckable(True)
        self.theme_toggle.setObjectName("theme-toggle")
        self.theme_toggle.setChecked(self.current_theme == "dark")
        
        # --- file label
        self.file_label = QLabel("No file selected")
        
        # --- progress bar
        self.progress = ProgressWidget()

        # --- output log
        self.output = LogView()

    def _build_layouts(self) -> None:
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
        # --- connect button actions
        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.export_btn.clicked.connect(self.export_file)
        self.clear_btn.clicked.connect(self.output.clear_logs)
        self.theme_toggle.clicked.connect(self.on_theme_toggle)

        # connect log link clicks
        self.output.anchorClicked.connect(self.handle_link_click)

    def _apply_defaults(self) -> None:
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

        if files: 
            self.file_paths = files
            names = [get_filename(f) for f in files]
            
            self.file_label.setText(f"{len(files)} file(s) selected")
            self.output.info(f"Selected files:")
            for name in names: self.output.log(f"  - {name}", log_time = False)

            self.minify_btn.setEnabled(True)

        else:
            # show warning
            self.output.warn(f"No target file selected")
            self.file_label.setText("No file selected")
            self.minify_btn.setEnabled(False)

    def run_minify(self) -> None:
        """
        Starts the asynchronous minification process.

        Creates a QThread and MinifyWorker to process selected files
        without blocking UI.

        Connects worker signals to UI handlers for:
        - progress updates
        - logging output
        - completion handling
        """

        if not self.file_paths: 
            self.output.warn(f"No target files specified")
            self.export_btn.setEnabled(False)
            return
        
        # disable buttons during processing and reset pgb
        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.progress.show_progress()
        self.progress.set_progress(0)

        self.output.info("Starting minification...")

        # create thread + worker
        self.mthread = QThread()
        self.worker = MinifyWorker(self.file_paths)

        self.worker.moveToThread(self.mthread)

        # connect signals
        self.mthread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_minify_finished)
        self.worker.progress.connect(self.progress.set_progress)
        
        self.worker.log.connect(self.output.log)
        self.worker.error.connect(self.output.error)
        self.worker.warn.connect(self.output.warn)
        self.worker.success.connect(self.output.success)
        self.worker.info.connect(self.output.info)

        # cleanup
        self.worker.finished.connect(self.mthread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.mthread.finished.connect(self.mthread.deleteLater)

        self.mthread.start()

    def export_file(self) -> None:
        """
        Exports minified results to a selected location.

        If a single file was processed, prompts for a save location.
        If multiple files processed, prompts for a folder.

        Writes minified content to files and displays confirmation or
        error messages in the log.
        """

        if not self.last_results:
            self.output.warn("Nothing to export")
            return
        
        # set the default directory
        default_dir = os.path.join(os.getcwd(), "generated")
        os.makedirs(default_dir, exist_ok = True)

        if len(self.last_results) == 1:
            path, content = self.last_results[0]
            name = get_filename(path)
            base, ext = os.path.splitext(name)
            default_name = f"{base}.min{ext}"

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Minified File",
                os.path.join(default_dir, default_name)
            )

            if not save_path: return

            try:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.last_export_dir = os.path.dirname(save_path)
                self.show_export_toast()

                self.output.success(
                    f"Exported: {get_filename(save_path)}",
                    link = save_path
                )

            except Exception as e:
                self.output.error(f"Export failed: {str(e)}")
        else:
            folder = QFileDialog.getExistingDirectory(
                self, 
                "Select Output Folder",
                default_dir
            )
            if not folder: return

            for path, content in self.last_results:
                try:
                    name = os.path.basename(path)
                    base, ext = os.path.splitext(name)
                    new_name = f"{base}.min{ext}"

                    output_path = os.path.join(folder, new_name)

                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    self.output.success(
                        f"Exported {new_name}",
                        link = output_path
                    )

                except Exception as e:
                    self.output.error(f"Export failed for {name}: {str(e)}")
            
            self.last_export_dir = folder
            self.show_export_toast()

    def on_minify_finished(self, results: list[tuple[str, str]]) -> None:
        """
        Handles completion of the minification process.

        Stores results, updates UI, re-enables controls, and 
        transitions progress UI back into idle state.

        Args:
            results: A list of the minified files in format of `[(path, content), ...]`
        """
        self.last_results = results

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
        if not self.last_export_dir:
            self.output.warn("No export folder available")
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(self.last_export_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.last_export_dir])
            else:
                subprocess.Popen(["xdg-open", self.last_export_dir])

            self.output.info("Opened output folder")

        except Exception as e:
            self.output.error(f"Failed to open folder: {str(e)}")

    def on_theme_toggle(self):
        """
        Actions to take when the toggle theme button is clicked.

        Inverts current theme of GUI smoothly.
        """
        is_dark = self.theme_toggle.isChecked()

        self.current_theme = "dark" if is_dark else "light"
        self.theme_toggle.setText("Light Mode" if is_dark else "Dark Mode")

        self.setUpdatesEnabled(False)
        self.apply_theme(self.current_theme)
        self.setUpdatesEnabled(True)

    # -------- HELPER FUNCTIONS ------------

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
        if not self.last_export_dir: return
        toast = Toast(self, "Open Output Folder")

        toast._on_click = self.open_output_folder
        toast.show_toast(self)

    def apply_theme(self, theme: str) -> None:
        """
        Applies the selected UI theme to the app.

        Args:
            theme: Theme name ("light" or "dark")

        Loads and applies the corresponding stylesheet globally
        """
        from PyQt6.QtWidgets import QApplication
        load_stylesheet(QApplication.instance(), theme)
        self.output.info(f"Successfully applied theme '{theme}'")

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

        # store urls in a list
        files = [url.toLocalFile() for url in event.mimeData().urls()]

        # ensure files exist
        if files:
            self.file_paths = files
            
            # update UI
            self.file_label.setText(f"{len(files)} file(s) selected")
            self.output.info("Files dropped:")
            for f in files: self.output.log(f"  - {get_filename(f)}")
            self.minify_btn.setEnabled(True)