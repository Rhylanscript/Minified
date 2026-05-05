# ui/main_window.py

# imports
import os
import subprocess
import sys

from datetime import datetime
from typing import override

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, 
    QTextBrowser, QHBoxLayout, QLabel, QGraphicsOpacityEffect,
    QProgressBar, QStackedLayout, QSizePolicy
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtCore import (
    QThread, QPropertyAnimation, QEasingCurve, 
    QTimer, QPoint, Qt
)

# import locals
from core.worker import MinifyWorker
from utils.util import get_filename
from ui.toast import Toast

class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # --- CLASS VARIABLES

        self.file_paths = []
        self.last_results = []
        
        self.last_export_dir = None
        self.log_text_color = "white"

        # config window
        self.setWindowTitle("Minified")
        self.resize(800, 500)

        self.setAcceptDrops(True)   # allow dropping of files onto the app

        main_layout = QHBoxLayout()      # create overall layout of app

        sidebar = QVBoxLayout()
        content = QVBoxLayout()

        # --- file section
        self.file_label = QLabel("No file selected")
        self.open_btn = QPushButton("Open File")

        # --- action buttons
        self.minify_btn = QPushButton("Minify")
        self.export_btn = QPushButton("Export")
        self.clear_btn = QPushButton("Clear Logs")

        # --- progress bar
        prb_height = 24

        self.progress_stack = QStackedLayout()
        self.progress_stack.setObjectName("progress-stack")

        self.progress_placeholder = QLabel("Minification progress will show here")
        self.progress_placeholder.setStyleSheet("color:#777;")
        self.progress_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_placeholder.setProperty("placeholder", True)
        self.progress_placeholder.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        progress_widget = QWidget()

        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 4, 0, 4)
        progress_layout.setSpacing(6)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_label = QLabel("0%")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.progress_label.setStyleSheet("margin: 0; padding: 0;")
        # self.progress_label.setFixedHeight(8)
        self.progress_label.setMinimumWidth(35)

        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)

        self.progress_stack.addWidget(self.progress_placeholder)
        self.progress_stack.addWidget(progress_widget)
        self.progress_stack.setCurrentIndex(0)

        # --- output log
        self.output = QTextBrowser()
        self.output.setObjectName("logBox")
        self.output.setOpenLinks(False)
        self.output.setOpenExternalLinks(False)
        self.output.anchorClicked.connect(self.handle_link_click)

        # log initialisation
        self.info("Minified Initialised")

        # --- add to layouts

        sidebar.addWidget(self.open_btn)
        sidebar.addWidget(self.minify_btn)
        sidebar.addWidget(self.export_btn)
        sidebar.addWidget(self.clear_btn)
        sidebar.addStretch()    # pushes buttons to top hopefully

        progress_container = QWidget()
        progress_container.setLayout(self.progress_stack)
        progress_container.setFixedHeight(prb_height)

        content.addWidget(self.file_label)
        content.addWidget(progress_container)
        content.addWidget(self.output)

        # connect button actions
        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.export_btn.clicked.connect(self.export_file)
        self.clear_btn.clicked.connect(self.clear_logs)

        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        # setup widget objects for panels
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(sidebar)

        # set layout
        main_layout.addWidget(sidebar_widget, 1)
        main_layout.addLayout(content, 4)

        self.setLayout(main_layout)

    # --------- BUTTON FUNCTIONS ----------
    def open_file(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self)

        if files: 
            self.file_paths = files
            names = [get_filename(f) for f in files]
            
            self.file_label.setText(f"{len(files)} file(s) selected")
            self.info(f"Selected files:")
            for name in names: self.log(f"  - {name}", log_time = False)

            self.minify_btn.setEnabled(True)

        else:
            self.warn(f"Failed to locate target file")
            self.file_label.setText("No file selected")
            self.minify_btn.setEnabled(False)

    def run_minify(self) -> None:
        if not self.file_paths: 
            self.warn(f"No target files specified")
            self.export_btn.setEnabled(False)
            return
        
        # disable buttons during processing and reset pgb
        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.progress_stack.setCurrentIndex(1)
        self.update_progress(0)

        self.info("Starting minification...")

        # create thread + worker
        self.mthread = QThread()
        self.worker = MinifyWorker(self.file_paths)

        self.worker.moveToThread(self.mthread)

        # connect signals
        self.mthread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_minify_finished)
        self.worker.progress.connect(self.update_progress)
        
        self.worker.log.connect(self.log)
        self.worker.error.connect(self.error)
        self.worker.warn.connect(self.warn)
        self.worker.success.connect(self.success)
        self.worker.info.connect(self.info)

        # cleanup
        self.worker.finished.connect(self.mthread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.mthread.finished.connect(self.mthread.deleteLater)

        self.mthread.start()

    def export_file(self) -> None:
        if not hasattr(self, "last_results") or not self.last_results:
            self.warn("Nothing to export")
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

                self.success(
                    f"Exported: {get_filename(save_path)}",
                    link = save_path
                )

            except Exception as e:
                self.error(f"Export failed: {str(e)}")
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

                    self.success(
                        f"Exported {new_name}",
                        link = output_path
                    )

                except Exception as e:
                    self.error(f"Export failed for {name}: {str(e)}")
            
            self.last_export_dir = folder
            self.show_export_toast()

    def on_minify_finished(self, results: list) -> None:
        self.last_results = results

        self.info("Minification complete")

        self.minify_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

        self.update_progress(100)
        QTimer.singleShot(800, lambda: self.progress_stack.setCurrentIndex(0))

    def open_output_folder(self) -> None:
        if not self.last_export_dir:
            self.warn("No export folder available")
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(self.last_export_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.last_export_dir])
            else:
                subprocess.Popen(["xdg-open", self.last_export_dir])

            self.info("Opened output folder")

        except Exception as e:
            self.error(f"Failed to open folder: {str(e)}")

    # -------- HELPER FUNCTIONS ------------
    def handle_link_click(self, url: str) -> None:
        path = url.toLocalFile()

        if not path:
            path = url.toString().replace("open://", "")

        try:
            if sys.platform == "win32":
                subprocess.Popen([f'explorer', '/select,', os.path.normpath(path)])
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(path)])
        
        except Exception as e:
            self.error(f"Failed to open file location: {str(e)}")

    def update_progress(self, value: int) -> None:
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{value}%")

    def show_export_toast(self) -> None:
        if not self.last_export_dir: return
        toast = Toast(self, "Open Output Folder")

        toast._on_click = self.open_output_folder
        toast.show_toast(self)

    # -------- OVERRIDES ---------

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData() and event.mimeData().hasUrls(): event.acceptProposedAction()

    @override
    def dropEvent(self, event: QDropEvent) -> None:
        if not event.mimeData(): return

        files = [url.toLocalFile() for url in event.mimeData().urls()]

        if files:
            self.file_paths = files

            self.file_label.setText(f"{len(files)} file(s) selected")

            self.info("Files dropped:")
            for f in files: self.log(f"  - {get_filename(f)}")

            self.minify_btn.setEnabled(True)

    # -------- LOGGING FUNCTIONS ---------

    def clear_logs(self) -> None:
        self.output.clear()
        self.info("Logs cleared successfully")

    def log(self, message: str, log_time: bool = True, link: str | None = None) -> None:

        timestamp = f"[{datetime.now().strftime("%H:%M:%S")}]" if log_time else ""

        # set log message
        if link:
            log_msg = (
                f"<font color={self.log_text_color}>"
                f"{timestamp} {message.replace(get_filename(link), '')}"
                f"<a href='file:///{os.path.abspath(link).replace("\\","/")}'>{get_filename(link)}</a>"
                f"</font>"
            )
        else: log_msg = f"<font color={self.log_text_color}>{timestamp} {message}</font>"

        self.output.append(log_msg)
        if self.output.verticalScrollBar():
            self.output.verticalScrollBar().setValue(
                self.output.verticalScrollBar().maximum()
            )

        # reset text colour to default
        self.log_text_color = "white"

    def error(self, message: str, log_time: bool = True, link: str | None = None) -> None:
        self.log_text_color = "#F02828"
        self.log(
            f"[ERROR] {message}", 
            log_time = log_time,
            link = link
        )

    def success(self, message: str, log_time: bool = True, link: str | None = None) -> None:
        self.log_text_color = "#0BF00B"
        self.log(
            f"[SUCCESS] {message}", 
            log_time = log_time,
            link = link
        )

    def warn(self, message: str, log_time: bool = True, link: str | None = None) -> None:
        self.log_text_color = "#FF9100"
        self.log(
            f"[WARNING] {message}", 
            log_time = log_time,
            link = link
        )

    def info(self, message: str, log_time: bool = True, link: str | None = None) -> None:
        self.log(
            f"[INFO] {message}", 
            log_time = log_time,
            link = link
        )