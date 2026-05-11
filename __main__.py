# __main__.py

"""
Application entrypoint.

Initialises the Qt Application, loads stylesheets, creates the
main window and starts the event loop.
"""

if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QSettings

    from ui.main_window import MainWindow
    from utils.style_loader import load_stylesheet

    def main() -> int:
        """
        Starts the application with a selected saved theme.

        Returns:
            Application exit code.
        """
        app = QApplication(sys.argv)

        # apply saved theme
        settings = QSettings("Minified", "Minified")
        saved_theme = settings.value("theme", "light")
        load_stylesheet(app, theme=saved_theme)

        # create window
        window = MainWindow(initial_theme=saved_theme)
        window.show()
        
        return app.exec()

    sys.exit(main())