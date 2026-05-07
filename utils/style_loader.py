# utils/style_loader.py

from utils.util import resource_path

from PyQt6.QtWidgets import QApplication

def load_stylesheet(
        app: QApplication, 
        theme: str = "dark", 
        base_path: str = "assets/styles/styles.qss" 
        # themes_path: str = "assets/themes"
    ) -> None:
    
    theme_path = f"assets/themes/{theme}.qss"

    try: 
        with open(resource_path(base_path), "r") as f: 
            base = f.read()

        with open(resource_path(theme_path), "r") as f:
            theme_css = f.read()

        app.setStyleSheet(base + "\n" + theme_css)

    except Exception as e:
        print(f"Failed to load stylesheet: {e}")