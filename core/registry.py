# core/registry.py

"""
Stores and manages registered file minifiers.

This file provides a central registry of available minifier
types and helper functions for retrieving the correct 
minifier based on file extension.
"""

from minifiers import *

# list of available minifiers
MINIFIERS: list[BaseMinifier] = [
    JSONMinifier(),
    HTMLMinifier(),
]

def get_minifier(file_extension: str) -> BaseMinifier | None: 
    """
    Retrieves the appropriate file minifier function given a
    file extension.

    Args:
        file_extension: File extension (INCLUDES the leading dot)
            (e.g. '.json', '.html')

    Returns:
        The matching minifier if one exists, otherwise
        returns None.
    """
    return next((m for m in MINIFIERS if file_extension.lower() in m.file_types), None)