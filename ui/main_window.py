# ui/main_window.py

import os

from typing import override
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, 
    QPlainTextEdit, QHBoxLayout, QLabel,
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
        self.resize(600, 400)

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
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setObjectName("logBox")
        
        self.log("[INFO] Minified Initialised")

        # --- add to main widget
        layout.addLayout(file_layout)
        layout.addLayout(action_layout)
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.file_paths = []
        self.last_results = []

        # connect button actions
        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.export_btn.clicked.connect(self.export_file)
        self.clear_btn.clicked.connect(self.clear_logs)

        self.minify_btn.setEnabled(False)
        self.export_btn.setEnabled(False)

    def open_file(self):
        files, _ = QFileDialog.getOpenFileNames(self)

        if files: 
            self.file_paths = files
            names = [get_filename(f) for f in files]
            
            self.file_label.setText(f"{len(files)} file(s) selected")
            self.log(f"[INFO] Selected files:")
            for name in names: self.log(f"  - {name}")

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
        
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not folder: return

        for path, content in self.last_results:
            try:
                name = os.path.basename(path)
                base, ext = os.path.splitext(name)
                new_name = f"{base}.min{ext}"

                output_path = os.path.join(folder, new_name)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.log(f"[SUCCESS] Exported {new_name}")

            except Exception as e:
                self.log(f"[ERROR] Export failed for {name}: {str(e)}")

    def clear_logs(self):
        self.output.clear()

    def log(self, message: str) -> None:
        self.output.appendPlainText(message)
        self.output.verticalScrollBar().setValue(self.output.verticalScrollBar().maximum())

    def on_minify_finished(self, results):
        self.last_results = results

        self.log("[INFO] Minification complete")

        self.minify_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

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
