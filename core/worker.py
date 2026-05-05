# core/worker.py

from PyQt6.QtCore import QObject, pyqtSignal
import os

from core.manager import minify_file
from utils.util import format_size, get_filename

class MinifyWorker(QObject):

    error   = pyqtSignal(str)
    warn    = pyqtSignal(str)
    success = pyqtSignal(str)
    info    = pyqtSignal(str)

    log = pyqtSignal(str)
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)

    # export_btn = pyqtSignal(bool)

    def __init__(self, file_paths: list) -> None:
        super().__init__()
        self.file_paths = file_paths

    def run(self) -> None:
        results = []

        total_original = 0
        total_minified = 0

        total_paths = len(self.file_paths)
        for i, path in enumerate(self.file_paths):
            try:
                original_size = os.path.getsize(path)

                result = minify_file(path)

                if type(result) == int: 
                    _, ext = os.path.splitext(path)
                    self.warn.emit(f"No minifier exists for '{ext}' files") 
                    continue
                
                results.append((path, result))

                minified_size = len(result.encode("utf-8"))

                total_original += original_size
                total_minified += minified_size

                reduction = (
                    100 * (original_size - minified_size) / original_size
                    if original_size > 0 else 0
                )

                preview_text = f"{result[:80]}..." if (len(result) > 80) else result

                self.success.emit(f"Minified {get_filename(path)}")
                self.success.emit(f"Preview: {preview_text}")
                self.info.emit(f"Size reduced from {format_size(original_size)} to {format_size(minified_size)} (-{reduction:.1f}%)")

            except Exception as e:
                self.error.emit(f"{get_filename(path)} : {str(e)}")
                self.error.emit(f"result : {result}" if result else "No result returned")
            finally:
                percent = int((i + 1) / total_paths * 100)
                self.progress.emit(percent)

        # summary
        if total_original > 0:
            total_reduction = 100 * (total_original - total_minified) / total_original
            self.log.emit("--------------------------------------------------")  #, log_time = False)
            self.info.emit(f"Total size reduced from {format_size(total_original)} to {format_size(total_minified)} (-{total_reduction:.1f}%)")

        self.finished.emit(results)