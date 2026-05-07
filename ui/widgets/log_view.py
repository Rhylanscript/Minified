# ui/widgets/log_view.py

"""
Custom logging widget for the application UI.

Provides formatible logging with:
- timestamps
- coloured messages
- clickable file links
- helper methods for logs
"""

import os

from datetime import datetime
from PyQt6.QtWidgets import QTextBrowser

from utils.util import get_filename

class LogView(QTextBrowser):
    """
    Rich text log view widget for the application that features
    multiple helper logging methods.
    """
    def __init__(self) -> None:
        super().__init__()

        self.setObjectName("logBox")
        self.setOpenLinks(False)
        self.setOpenExternalLinks(False)

    def clear_logs(self) -> None:
        """Simple method to clear the logs."""
        self.clear()
        self.info("Logs cleared successfully")

    def log(
            self, 
            message: str, 
            log_time: bool = True, 
            link: str | None = None,
            color: str | None = None
        ) -> None:
        """
        Appends a formatted message the the output log.

        Supports:
        - Timestamps
        - Clickable file links
        - Coloured text output

        Args:
            message: The default message to add to the logs
            log_time: Flag argument to specify whether to prefix with timestamp
            link: Optional file path to make text clickable
            color: Optional HTML color for message styling
        """
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}]" if log_time else ""
        full_message = f"{timestamp} {message}"

        # set full log message
        if link:
            full_message = (
                f"{timestamp}"
                f"{message.replace(get_filename(link), '')}"
                f"<a href='file:///{os.path.abspath(link).replace('\\', '/')}'>{get_filename(link)}</a>"
            )
        if color: full_message = f"<span style='color:{color};'>{full_message}</span>"

        self.append(full_message)

        scrollbar = self.verticalScrollBar()
        if scrollbar: scrollbar.setValue(scrollbar.maximum())

    def error(self, message: str, **kwargs) -> None:
        """
        Show a red error message in output log.

        Args:
            message: The message to append to logs
        """
        self.log(f"[ERROR] {message}", color = "#F02828", **kwargs)

    def success(self, message: str, **kwargs) -> None:
        """
        Show a green success message in output log.

        Args:
            message: The message to append to logs
        """
        self.log(f"[SUCCESS] {message}", color = "#07DA07", **kwargs)

    def warn(self, message: str, **kwargs) -> None:
        """
        Show a yellow warning message in output log.

        Args:
            message: The message to append to logs
        """
        self.log(f"[WARNING] {message}", color = "#E0840B", **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """
        Show a themed message in output log.

        Args:
            message: The message to append to logs
        """
        self.log(f"[INFO] {message}", **kwargs)