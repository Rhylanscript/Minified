# ui/main_window.py

# imports
import os
import subprocess
import sys

from datetime import datetime
from typing import override
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, 
    QTextBrowser, QHBoxLayout, QLabel, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtCore import QThread, QPropertyAnimation, QEasingCurve, QTimer, QPoint

# import locals
from core.worker import MinifyWorker
from utils.util import get_filename

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

        self.setAcceptDrops(True)

        layout = QVBoxLayout()

        # --- file section
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        self.open_btn = QPushButton("Open File")

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.open_btn)

        # --- action buttons
        action_layout = QHBoxLayout()
        self.minify_btn = QPushButton("Minify")
        self.export_btn = QPushButton("Export")
        self.clear_btn = QPushButton("Clear Logs")

        action_layout.addWidget(self.minify_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.clear_btn)

        # --- output log
        self.output = QTextBrowser()
        # self.output.setReadOnly(True)

        self.output.setObjectName("logBox")
        self.output.setOpenLinks(False)
        self.output.setOpenExternalLinks(False)
        self.output.anchorClicked.connect(self.handle_link_click)

        # log initialisation
        self.info("Minified Initialised")

        # self.warn("testing warnings")
        # self.error("testing errors")
        # self.success("testing success")

        # --- add to main widget
        layout.addLayout(file_layout)
        layout.addLayout(action_layout)
        layout.addWidget(self.output)

        self.setLayout(layout)

        # connect button actions
        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.export_btn.clicked.connect(self.export_file)
        self.clear_btn.clicked.connect(self.clear_logs)

        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

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
            self.error(f"Failed to target file")
            self.file_label.setText("No file selected")
            self.minify_btn.setEnabled(False)

    def run_minify(self) -> None:
        if not self.file_paths: 
            self.warn(f"No target files specified")
            self.export_btn.setEnabled(False)
            return
        
        # disable buttons during processing
        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.info("Starting minification...")

        # create thread + worker
        self.mthread = QThread()
        self.worker = MinifyWorker(self.file_paths)

        self.worker.moveToThread(self.mthread)

        # connect signals
        self.mthread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_minify_finished)
        
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

    def on_minify_finished(self, results) -> None:
        self.last_results = results

        self.info("Minification complete")

        self.minify_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

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

    def handle_link_click(self, url):
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

    def show_export_toast(self):
        if not self.last_export_dir: return

        if hasattr(self, "toast") and self.toast:
            try:
                self.toast.hide()
                self.toast.deleteLater()
            except RuntimeError:...
            self.toast = None

        # make toast
        self.toast = QLabel("Open Output Folder", self)
        self.toast.setObjectName("exportToast")
        
        self.opacity_effect = QGraphicsOpacityEffect(self.toast)
        self.toast.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        self.toast.adjustSize()

        # position in bottom right
        margin = 20
        x = self.width() - self.toast.width() - margin
        y = self.height() - self.toast.height() - margin
        self.toast.move(x, y)

        self.toast.show()
        self.toast.raise_()

        # click to open folder
        self.toast.mousePressEvent = lambda e: self.open_output_folder()

        # FADE IN ANIMATION
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_anim.setDuration(300)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_in_anim.start()

        # store timer
        if hasattr(self, "toast_timer"): self.toast_timer.stop()
        self.toast_timer = QTimer(self)
        self.toast_timer.setSingleShot(True)

        # FADE OUT ANIMATION
        self.toast_timer.timeout.connect(self.fade_out_toast)
        self.toast_timer.start(2500)

    def fade_out_toast(self):

        if not hasattr(self, "toast") or not self.toast: return

        try:
            self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
            self.fade_out_anim.setDuration(500)
            self.fade_out_anim.setStartValue(1)
            self.fade_out_anim.setEndValue(0)
            self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

            def cleanup():
                if self.toast:
                    self.toast.deleteLater()
                    self.toast = None

            self.fade_out_anim.finished.connect(cleanup)
            self.fade_out_anim.start()

        except RuntimeError:

            # widget probably already deleted so just ignore it
            self.toast = None


    # -------- OVERRIDES ---------

    @override
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    @override
    def dropEvent(self, event: QDropEvent) -> None:
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