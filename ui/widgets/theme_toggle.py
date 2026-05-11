# ui/widgets/theme_toggle.py

"""
Custom button widget to toggle application theme.

Has the `ThemeToggle` class which controls logic around themes
and switching them throughout runtime.
"""

from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtWidgets import QPushButton, QApplication

from utils.style_loader import load_stylesheet

class ThemeToggle(QPushButton):

    """
    A custom widget for the application.

    This widget controls the application theme and has logic to
    change it when clicked, while emitting that change where
    needed. It applies the stylesheet for theming directly too.
    """

    # signal to notify app of theme change
    theme_changed = pyqtSignal(str)

    def __init__(self, theme: str = "light") -> None:
        super().__init__()

        self.current_theme = theme

        self.setCheckable(True)
        self.setObjectName("theme-toggle")
        self.setChecked(theme == "dark")

        self.clicked.connect(self.toggle_theme)

        self._update_text()

    def toggle_theme(self) -> None:
        """Method to toggle theme between light and dark mode."""
        is_dark = self.isChecked()
        self.current_theme = "dark" if is_dark else "light"

        self._update_text()

        # save theme
        settings = QSettings("Minified", "Minified")
        settings.setValue("theme", self.current_theme)

        load_stylesheet(QApplication.instance(), self.current_theme)
        self.theme_changed.emit(self.current_theme)

    def _update_text(self) -> None:
        """Update button text based on current theme."""
        self.setText(
            "Light Mode"
            if self.current_theme == "dark"
            else "Dark"
        )