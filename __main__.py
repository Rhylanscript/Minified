# __main__.py

if __name__ == "__main__":
    import sys
    
    from PyQt6.QtWidgets import QApplication
    
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())