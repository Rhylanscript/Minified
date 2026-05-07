# ui/widgets/progress_widget.py

"""
Custom progress bar widget for the app UI.

Houses the `ProgressWidget` class which shows the progress of
minification tasks, and its setup for ui and logic.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QLabel, QHBoxLayout, 
    QProgressBar, QStackedLayout, QSizePolicy
)

class ProgressWidget(QWidget):
    """
    Widget containing:
    - placeholder text
    - progress bar
    - percentage label

    Shows the progress of ongoing minification tasks.
    """

    def __init__(self) -> None:
        super().__init__()

        self.bar_height: int = 24

        # create the stack (0 off | 1 on)
        self.stack = QStackedLayout()
        self.stack.setObjectName("progress-stack")

        # --- idle widget
        self.placeholder = QLabel("Minification progress will show here")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setProperty("placeholder", True)
        # self.placeholder.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # --- active widget
        progress_widget = QWidget()

        # create the layout of the active widget and assign to widget
        layout = QHBoxLayout(progress_widget)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(6)

        # progress bar
        self.bar = QProgressBar()
        self.bar.setTextVisible(False)
        self.bar.setValue(0)

        # percentage label
        self.label = QLabel("0%")
        self.label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.label.setObjectName("progress-label")
        self.label.setMinimumWidth(35)

        # add widgets to layout
        layout.addWidget(self.bar)
        layout.addWidget(self.label)

        # add widgets to stack in order
        self.stack.addWidget(self.placeholder)
        self.stack.addWidget(progress_widget)

        # assign layout and set size
        self.setLayout(self.stack)
        self.setFixedHeight(self.bar_height)

        # show default state
        self.show_idle()

    def set_progress(self, value: int) -> None:
        """
        Update the progress bar and progress label with a specified
        value to display.

        Args:
            value: The value to display
        """
        self.bar.setValue(value)
        self.label.setText(f"{value}%")

    def show_progress(self) -> None:
        """Show the progress bar widget in the stack."""
        self.stack.setCurrentIndex(1)

    def show_idle(self) -> None:
        """Show the placeholder widget in the stack."""
        self.stack.setCurrentIndex(0)