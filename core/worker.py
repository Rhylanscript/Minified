# core/worker.py

"""
Asynchronous worker that will run on a QThread for minifying
multiple files.

Runs file minification in the background via a Qt thread-safe
QObject which emits progress, logs, warnings and results
through the pyqtSignals it connects.
"""

from PyQt6.QtCore import QObject, pyqtSignal
import os

from core.manager import minify_file
from utils.util import format_size, get_filename

class MinifyWorker(QObject):

    """
    Qt worker object that asynchronously minifies files.

    This worker processes a list of file paths, and minifies each file
    using the correct registered minifier, while emitting signals to
    report back to the application:

    - progress updates
    - success and error messages
    - warnings for unsupported filetypes
    - final results and summary stats

    Intended to be run in a separate thread in order to not block the UI
    """

    error   = pyqtSignal(str)
    warn    = pyqtSignal(str)
    success = pyqtSignal(str)
    info    = pyqtSignal(str)

    log = pyqtSignal(str)
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)

    def __init__(self, file_paths: list[str]) -> None:
        super().__init__()
        self.file_paths = file_paths

    def run(self) -> None:
        """
        Executes the file minification process.

        For each file in the provided file list:
        - Read the file size
        - Attempt to minify content using a registered minifier
        - Emit warnings if no registered minfier exists
        - Tracks original vs minfied file sizes
        - Emits success info and error signals

        Progress is reported incrementally as a percentage.

        At completion:
        - Emits a summary
        - Emits a list of (file_path, minified_content) results
        - Emits the finished signal 
        """
        results = []

        total_original = 0
        total_minified = 0

        total_paths = len(self.file_paths)

        # enumerate through the list of paths
        for i, path in enumerate(self.file_paths):
            result = None

            try:
                original_size = os.path.getsize(path)
                result = minify_file(path)

                # ensure the correct minfier exists
                if isinstance(result, int): 
                    ext = os.path.splitext(path)[1]
                    self.warn.emit(f"No minifier exists for '{ext}' files") 
                    continue
                
                results.append((path, result))

                # track file sizes & show size reduction
                minified_size = len(result.encode("utf-8"))
                total_original += original_size
                total_minified += minified_size

                reduction = (
                    100 * (original_size - minified_size) / original_size
                    if original_size > 0 else 0
                )

                # show a preview of the file in logs and the summary of the current file
                preview_text = f"{result[:80]}..." if (len(result) > 80) else result

                self.success.emit(f"Minified {get_filename(path)}")
                self.success.emit(f"Preview: {preview_text}")
                self.info.emit(f"Size reduced from {format_size(original_size)} to {format_size(minified_size)} (-{reduction:.1f}%)")

            except Exception as e:
                # show any errors in logs
                self.error.emit(f"{get_filename(path)} : {str(e)}")
                self.error.emit(f"result : {result}" if result else "No result returned")
            finally:
                # show minification progress 
                percent = int((i + 1) / total_paths * 100)
                self.progress.emit(percent)

        # summarise total results
        if total_original > 0:
            total_reduction = 100 * (total_original - total_minified) / total_original
            #self.log.emit("--------------------------------------------------")  #, log_time = False)
            self.info.emit(f"Total size reduced from {format_size(total_original)} to {format_size(total_minified)} (-{total_reduction:.1f}%)")

        # emit the finished signal
        self.finished.emit(results)