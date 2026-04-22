# ui/main_window.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QPlainTextEdit
)

from core.manager import minify_file
from utils.util import get_filename

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Minified")

        layout = QVBoxLayout()

        self.open_btn = QPushButton("Open File")
        self.minify_btn = QPushButton("Minify")
        self.clear_btn = QPushButton("Clear Logs")

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        layout.addWidget(self.open_btn)
        layout.addWidget(self.minify_btn)
        layout.addWidget(self.output)
        layout.addWidget(self.clear_btn)

        self.setLayout(layout)

        self.file_path = None

        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.clear_btn.clicked.connect(self.clear_logs)

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self)
        if file: 
            self.file_path = file
            self.log(f"[INFO] Selected file: {get_filename(str(file))}")
        else:
            self.log(f"[ERROR] Failed to target file")

    def run_minify(self):
        if not self.file_path: 
            self.log(f"[WARN] No target file specified")
            return

        try:
            result = minify_file(self.file_path)
            self.log(f"[SUCCESS] Successfully minified {get_filename(self.file_path)}: {result}")

        except Exception as e:
            self.log(f"[ERROR] {str(e)}")

    def clear_logs(self):
        self.output.clear()

    def log(self, message: str) -> None:
        self.output.appendPlainText(message)
