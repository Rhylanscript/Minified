# ui/toast.py

"""
Animated toast notification widget.

Provides a lightweight temporary popup message with fadein and
fadeout animations. Toasts are displayed relative to a parent
widget and automatically disappear after a configurable duration.

Supports optional click callbacks for interactive notifications.
"""

from PyQt6.QtWidgets import QLabel, QApplication, QGraphicsOpacityEffect, QWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QTimer, QEvent

from typing import override

class Toast(QLabel):
    """
    Small animated popup notification widget.

    Displays a temporary message overlay with smooth fade 
    animations and optional click handling.

    Features:
    - Fadein and Fadeout animations
    - Automatic timed dismissal
    - Optional click callback support
    - Relative positioning inside parent widget
    """
    def __init__(self, parent: QWidget, message: str, duration: int = 5000) -> None:
        """
        Initialises the toast notification widget.

        Args:
            parent: Parent widget used for positioning and ownership
            message: Text displayed inside the toast
            duration: Duration in ms before fading out (defaults to 5s)
        """
        super().__init__(message, parent)

        self.setObjectName("toast") # for styling
        self.duration = duration

        self._on_click = None

        # --- ANIMATIONS
        # OPACITY EFFECT FOR FADES
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

        # ANIMATE IN
        self.fade_in_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.fade_in_anim.setDuration(300)
        self.fade_in_anim.setStartValue(0)
        self.fade_in_anim.setEndValue(1)
        self.fade_in_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # ANIMATE OUT
        self.fade_out_anim = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.fade_out_anim.setDuration(500)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # connect
        self.fade_out_anim.finished.connect(self.cleanup)

        # timer
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.start_fade_out)

    def cleanup(self) -> None: 
        """Schedules the toast widget for deletion."""
        self.deleteLater()
    def start_fade_out(self) -> None: 
        """Starts the fadeout animation."""
        self.fade_out_anim.start()

    def show_toast(self, parent: QWidget, margin: int = 20) -> None:
        """
        Displays the toast inside the parent widget.

        The toast is positioned near the bottom right corner of the parent
        with configurable margins (default 20).

        Args:
            parent: Widget used for positioning reference
            margin: Difference from the window edges in pixels
        """
        self.adjustSize()

        parent_rect = parent.rect()
        x = parent_rect.width() - self.width() - margin
        y = parent_rect.height() - self.height() - margin

        self.move(x, y)

        self.show()
        self.raise_()

        self.fade_in_anim.start()
        self.timer.start(self.duration)

    @override
    def mousePressEvent(self, ev: QEvent) -> None:
        """
        Handles toast click events.

        Executes the optional click callback if one is assigned. Overrides 
        from parent class `QLabel`.
        """
        if hasattr(self, "_on_click"):
            self._on_click()