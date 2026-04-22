# core/worker.py

from PyQt6.QtCore import QObject, pyqtSignal
import os

from core.manager import minify_file
from utils.util import format_size, get_filename

class MinifyWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal(list)

    # export_btn = pyqtSignal(bool)

    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths

    def run(self):
        results = []

        total_original = 0
        total_minified = 0

        for path in self.file_paths:
            try:
                original_size = os.path.getsize(path)

                result = minify_file(path)
                results.append((path, result))

                minified_size = len(result.encode("utf-8"))

                total_original += original_size
                total_minified += minified_size

                reduction = (
                    100 * (original_size - minified_size) / original_size
                    if original_size > 0 else 0
                )

                preview_text = f"{result[:80]}..." if (len(result) > 80) else result

                self.log.emit(f"[SUCCESS] Minified {get_filename(path)}")
                self.log.emit(f"[SUCCESS] Preview: {preview_text}")
                self.log.emit(f"[INFO] Size reduced from {format_size(original_size)} to {format_size(minified_size)} (-{reduction:.1f}%)")

            except Exception as e:
                self.log(f"[ERROR] {get_filename(path)} : {str(e)}")

        # summary
        if total_original > 0:
            total_reduction = 100 * (total_original - total_minified) / total_original
            self.log.emit("--------------------------------------------------")
            self.log.emit(f"[INFO] Total size reduced from {format_size(total_original)} to {format_size(total_minified)} (-{reduction:.1f}%)")

        self.finished.emit(results)