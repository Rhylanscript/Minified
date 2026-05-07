# core/task_manager.py

"""
Manages tasks in the application.

Has the TaskManager class which is responsible for handling
workers and threads of the application.
"""

from PyQt6.QtCore import QObject, QThread

from core.worker import MinifyWorker

from functools import partial

class TaskManager(QObject):
    """
    Handles worker/thread management.

    Creates workers and assigns them threads, killing them once
    they finish for background tasks.
    """
    def __init__(self) -> None:
        super().__init__()

        self.threads: list[QThread] = []
        self.workers: list[MinifyWorker] = []

    def start_minify(self, files: list[str]) -> MinifyWorker:
        """
        Create and start a worker for minification.

        Args:
            files: Files to process

        Returns:
            The created worker instance.
        """

        thread = QThread()
        worker = MinifyWorker(files)

        worker.moveToThread(thread)

        # add instances to lists
        self.threads.append(thread)
        self.workers.append(worker)

        # start worker
        thread.started.connect(worker.run)

        # cleanup
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.finished.connect(partial(self._cleanup, thread, worker))

        # start thread
        thread.start()

        return worker
    
    def is_busy(self) -> bool:
        """
        Simple method to determine if minification already running.

        Returns:
            Boolean showing minification state.
        """
        return len(self.threads) > 0
    
    def _cleanup(self, thread: QThread, worker: MinifyWorker) -> None:
        """
        Remove completed thread and worker references

        Args:
            thread: Thread instance
            worker: Worker instance
        """
        if thread in self.threads: self.threads.remove(thread)
        if worker in self.workers: self.workers.remove(worker)