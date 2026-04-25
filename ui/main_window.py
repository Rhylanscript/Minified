# ui/main_window.py

import os
import subprocess
import sys

from datetime import datetime
from typing import override
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, 
    QTextBrowser, QHBoxLayout, QLabel,
)

from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtCore import QThread

from core.worker import MinifyWorker
from utils.util import get_filename

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

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

        # open folder button
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.open_folder_btn.setEnabled(False)

        action_layout.addWidget(self.minify_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.clear_btn)
        action_layout.addWidget(self.open_folder_btn)

        # --- output log
        self.output = QTextBrowser()
        # self.output.setReadOnly(True)
        self.output.setObjectName("logBox")
        self.output.setOpenExternalLinks(True)

        # log initialisation
        self.log("[INFO] Minified Initialised")

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
        self.open_folder_btn.clicked.connect(self.open_output_folder)

        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        # --- CLASS VARIABLES

        self.file_paths = []
        self.last_results = []
        
        self.last_export_dir = None

    def open_file(self):
        files, _ = QFileDialog.getOpenFileNames(self)

        if files: 
            self.file_paths = files
            names = [get_filename(f) for f in files]
            
            self.file_label.setText(f"{len(files)} file(s) selected")
            self.log(f"[INFO] Selected files:")
            for name in names: self.log(f"  - {name}", log_time = False)

            self.minify_btn.setEnabled(True)

        else:
            self.log(f"[ERROR] Failed to target file")
            self.file_label.setText("No file selected")
            self.minify_btn.setEnabled(False)

    def run_minify(self):
        if not self.file_paths: 
            self.log(f"[WARN] No target files specified")
            self.export_btn.setEnabled(False)
            return
        
        # disable buttons during processing
        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

        self.log("[INFO] Starting minification...")

        # create thread + worker
        self.mthread = QThread()
        self.worker = MinifyWorker(self.file_paths)

        self.worker.moveToThread(self.mthread)

        # connect signals
        self.mthread.started.connect(self.worker.run)
        self.worker.log.connect(self.log)
        self.worker.finished.connect(self.on_minify_finished)

        # cleanup
        self.worker.finished.connect(self.mthread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.mthread.finished.connect(self.mthread.deleteLater)

        self.mthread.start()

    def export_file(self):
        if not hasattr(self, "last_results") or not self.last_results:
            self.log("[WARN] Nothing to export")
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
                self.open_folder_btn.setEnabled(True)

                self.log(
                    f"[SUCCESS] Exported: {get_filename(save_path)}",
                    link = save_path
                )

            except Exception as e:
                self.log(f"[ERROR] Export failed: {str(e)}")
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

                    self.log(
                        f"[SUCCESS] Exported {new_name}",
                        link = output_path
                    )

                except Exception as e:
                    self.log(f"[ERROR] Export failed for {name}: {str(e)}")
            
            self.last_export_dir = folder
            self.open_folder_btn.setEnabled(True)

    def clear_logs(self):
        self.output.clear()

    def log(self, message: str, log_time: bool = True, link: str | None = None) -> None:
        timestamp = f"[{datetime.now().strftime("%H:%M:%S")}]" if log_time else ""

        if link:
            log_msg = f"{timestamp} {message} <a href='file:///{link}'>[open]</a>"
        else:
            log_msg = f"{timestamp} {message}"

        self.output.append(log_msg)
        self.output.verticalScrollBar().setValue(
            self.output.verticalScrollBar().maximum()
        )

    def on_minify_finished(self, results):
        self.last_results = results

        self.log("[INFO] Minification complete")

        self.minify_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

    def open_output_folder(self):
        if not self.last_export_dir:
            self.log("[WARN] No export folder available")
            return
        
        try:
            if sys.platform == "win32":
                os.startfile(self.last_export_dir)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.last_export_dir])
            else:
                subprocess.Popen(["xdg-open", self.last_export_dir])

            self.log("[INFO] Opened output folder")

        except Exception as e:
            self.log(f"[ERROR] Failed to open folder: {str(e)}")

    @override
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    @override
    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]

        if files:
            self.file_paths = files

            self.file_label.setText(f"{len(files)} file(s) selected")

            self.log("[INFO] Files dropped:")
            for f in files: self.log(f"  - {get_filename(f)}")

            self.minify_btn.setEnabled(True)
