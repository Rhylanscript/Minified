# __main__.py

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    from ui.main_window import MainWindow
    from utils.style_loader import load_stylesheet

    theme = "light"

    app = QApplication(sys.argv)
    load_stylesheet(app, theme = theme)

    window = MainWindow(initial_theme = theme)
    window.show()
    
    sys.exit(app.exec())