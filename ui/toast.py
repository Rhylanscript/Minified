# ui/toast.py

from PyQt6.QtWidgets import QLabel, QApplication, QGraphicsOpacityEffect, QWidget
from PyQt6.QtCore import (
    QPropertyAnimation, QEasingCurve, QTimer, QEvent
)

class Toast(QLabel):
    def __init__(self, parent: QWidget, message: str, duration: int = 5000) -> None:
        super().__init__(message, parent)

        self.setObjectName("toast") # for styles.qss
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

    # helper methods to manage events
    def cleanup(self) -> None: self.deleteLater()
    def start_fade_out(self) -> None: self.fade_out_anim.start()

    # method to show the toast at given coordinates
    def show_toast(self, parent: QWidget, margin: int = 20) -> None:
        self.adjustSize()

        parent_rect = parent.rect()
        x = parent_rect.width() - self.width() - margin
        y = parent_rect.height() - self.height() - margin

        self.move(x, y)

        self.show()
        self.raise_()

        self.fade_in_anim.start()
        self.timer.start(self.duration)

    def mousePressEvent(self, ev: QEvent) -> None:
        if hasattr(self, "_on_click"):
            self._on_click()