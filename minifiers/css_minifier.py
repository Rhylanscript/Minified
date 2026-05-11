# minifiers/css_minifier.py

"""
CSS Minifier Implementation.

Converts CSS content into a much more compact form by removing
all unnecessary newlines, whitespace and comments while 
preserving valid structure.
"""

import re

from typing import override
from minifiers.base import BaseMinifier

class CSSMinifier(BaseMinifier):
    """
    Minifier for CSS files.

    Supports:
    - .css

    Converts formatted CSS into a compacted string version by 
    removing unecessary whitespace, newlines and comments while
    maintaining a valid CSS structure.
    """
    file_types = [".css"]

    @override
    def minify(self, content: str) -> str:
        """
        Minifies CSS content by removing unecessary characters.

        The process works by:
        - Collecting the input as a string
        - Using the `re` library to use regex to eliminate extra characters
        - Returns the finalised string

        Args:
            content: Raw CSS string

        Returns:
            A compacted CSS string
        """
        # remove comments
        content = re.sub(r"/\*.*?\*/", "", content, flags = re.DOTALL)

        # remove whitespace around symbols and collapse any remaining whitespace
        content = re.sub(r"\s*([{}:;,])\s*", r"\1", content)
        content = re.sub(r"\s+", " ", content)

        # return finalised CSS string
        return content.strip()