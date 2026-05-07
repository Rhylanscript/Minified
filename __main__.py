# __main__.py

"""
Application entrypoint.

Initialises the Qt Application, loads stylesheets, creates the
main window and starts the event loop.
"""

if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication

    from ui.main_window import MainWindow
    from utils.style_loader import load_stylesheet

    DEFAULT_THEME = "dark"

    def main() -> int:
        """
        Starts the application.

        Returns:
            Application exit code.
        """
        app = QApplication(sys.argv)
        load_stylesheet(app, theme = DEFAULT_THEME)

        window = MainWindow(initial_theme = DEFAULT_THEME)
        window.show()
        
        return app.exec()

    sys.exit(main())