# ui/widgets/sidebar.py

"""
Custom sidebar widget that houses other widgets.

Is placed on the left side of screen in order to organise
all the action buttons together.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from ui.widgets.theme_toggle import ThemeToggle

class Sidebar(QWidget):
    """
    Sidebar custom widget that contains application controls.

    Controls include:
    - Open file button
    - Minify button
    - Export button
    - Clear logs button
    - Toggle theme button
    """
    def __init__(self, initial_theme: str = "light") -> None:
        super().__init__()

        self.setObjectName("sidebar")

        self._build_widgets(initial_theme=initial_theme)
        self._build_layouts()

    def _build_widgets(self, initial_theme: str = "light") -> None:
        """Create sidebar widgets."""
        self.open_btn = QPushButton("Open File")
        self.minify_btn = QPushButton("Minify")
        self.export_btn = QPushButton("Export")
        self.clear_btn = QPushButton("Clear Logs")

        self.theme_toggle = ThemeToggle(theme=initial_theme)

    def _build_layouts(self) -> None:
        """Build the sidebar layout"""
        layout = QVBoxLayout()

        layout.addWidget(self.open_btn)
        layout.addWidget(self.minify_btn)
        layout.addWidget(self.export_btn)
        layout.addWidget(self.clear_btn)

        layout.addStretch()

        layout.addWidget(self.theme_toggle)

        self.setLayout(layout)