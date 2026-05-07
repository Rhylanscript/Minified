# utils/style_loader.py

"""
Stylesheet loading utilities.

Provides helper functions for loading and applying Qt stylesheets 
(.qss) coupled with the theme stylesheets. 
"""

from utils.util import resource_path

from PyQt6.QtWidgets import QApplication

def load_stylesheet(
        app: QApplication, 
        theme: str = "dark", 
        base_path: str = "assets/styles/styles.qss",
        themes_path: str = "assets/themes/"
    ) -> None:

    """
    Loads and applies application stylesheets.

    Combines the shared base stylesheet (by default `styles.qss`) with
    the specified theme stylesheet and applies the result globally to
    the QApplication instance.

    Any file loading errors will be caught and printed to the console.
    
    Args:
        app: The instance of QApplication to apply the styles to
        theme: Theme name used to select the theme stylesheet
        base_path: The path to the base stylesheet file
        themes_path: The path to the themes directory
    """
    
    theme_path = f"{themes_path}/{theme}.qss"

    try: 
        with open(resource_path(base_path), "r") as f: 
            base = f.read()

        with open(resource_path(theme_path), "r") as f:
            theme_css = f.read()

        app.setStyleSheet(base + "\n" + theme_css)

    except Exception as e:
        print(f"Failed to load stylesheet: {e}")