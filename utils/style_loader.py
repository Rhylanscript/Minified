# utils/style_loader.py

import os
import sys

from utils.util import resource_path
from PyQt6.QtWidgets import QApplication

def load_stylesheet(app: QApplication, path="assets/styles.qss"):
    try:
        with open(resource_path(path), "r") as f:
            app.setStyleSheet(f.read())

    except Exception as e:
        print(f"Failed to load stylesheet: {e}")