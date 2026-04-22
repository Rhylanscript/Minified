# ui/main_window.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, 
    QPlainTextEdit, QHBoxLayout, QLabel
)

from core.manager import minify_file
from utils.util import get_filename

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # config window
        self.setWindowTitle("Minified")
        self.resize(600, 400)

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

        # --- add to main widget
        layout.addLayout(file_layout)
        layout.addLayout(action_layout)
        layout.addWidget(self.output)

        self.setLayout(layout)

        self.file_path = None
        self.last_result = None

        # connect button actions
        self.open_btn.clicked.connect(self.open_file)
        self.minify_btn.clicked.connect(self.run_minify)
        self.export_btn.clicked.connect(self.export_file)
        self.clear_btn.clicked.connect(self.clear_logs)

    def open_file(self):
        file, _ = QFileDialog.getOpenFileName(self)
        if file: 
            self.file_path = file
            self.file_label.setText(get_filename(str(file)))
            self.log(f"[INFO] Selected file: {get_filename(str(file))}")
        else:
            self.log(f"[ERROR] Failed to target file")
            self.file_label.setText("No file selected")

    def run_minify(self):
        if not self.file_path: 
            self.log(f"[WARN] No target file specified")
            return

        try:
            result = minify_file(self.file_path)
            self.last_result = result

            self.log(f"[SUCCESS] Successfully minified {get_filename(self.file_path)}")
            self.log(f"[SUCCESS] Preview: {result[:100]}...")

        except Exception as e:
            self.log(f"[ERROR] {str(e)}")

    def export_file(self):
        if not self.last_result:
            self.log("[WARN] Nothing to export")
            return
        
        file, _ = QFileDialog.getSaveFileName(
            self,
            "Save Minified File",
            f"generated/{get_filename(self.file_path.replace(".", ".min."))}"
        )

        if file:
            try:
                with open(file, "w", encoding="utf-8") as f:
                    f.write(self.last_result)

                self.log(f"[SUCCESS] Exported to: {file}")

            except Exception as e:
                self.log(f"[ERROR] Export failed: {str(e)}")

    def clear_logs(self):
        self.output.clear()

    def log(self, message: str) -> None:
        self.output.appendPlainText(message)
