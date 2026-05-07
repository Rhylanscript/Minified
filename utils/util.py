# utils/util.py

"""
General utility helper functions.

Provides useful and reusable helpers for:
- file path handling
- Human-Readable file size formatting
"""

import os
import sys

def get_filename(path: str) -> str: 
    """
    Extracts the filename from a file path.

    Args:
        path: Full file path
    
    Returns:
        Filename portion of the path.
    """
    return os.path.basename(path)

def resource_path(relative_path: str) -> str:
    """
    Resolves the absolute path to a resource.

    Primarily used for getting the path to a `.qss` file.

    Args:
        relative_path: Relative path to the resource.

    Returns:
        Absolute path of the resource file.
    """
    try:
        base_path = sys._MEIPASS

    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def format_size(num_bytes: int) -> str:
    """
    Converts a byte count into human readable size string.

    Automatically convert values to:
    - B
    - KB
    - MB
    - GB
    - TB

    Args:
        num_bytes: Size in bytes

    Returns:
        Human readable formatted size string
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"