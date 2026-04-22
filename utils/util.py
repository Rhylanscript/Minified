import os
import sys

def get_filename(path):
    return os.path.basename(path)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS

    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)