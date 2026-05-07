# minifiers/html_minifier.py

"""
HTML minifier implementation.

Removes uncessary whitespace from HTML content while preserving
structure and tag integrity.

This minifier is lightweight and focuses on basic whitespace
compression 🗜️ rather than full HTML optimisation.
"""

import re

from typing import override
from minifiers.base import BaseMinifier

class HTMLMinifier(BaseMinifier):
    """
    Minifier for HTML files.

    ## Supports:
    - .html
    - .htm

    Performs basic whitespace reduction between tags and inside HTML content
    to reduce file size while keeping valid structure.

    ## WARNING
    This minifier does NOT preserve `pre` or `code` whitespace!
    """

    file_types = [".html", ".htm"]

    @override
    def minify(self, content: str) -> str:
        """
        Minifies HTML content by removing unecessary whitespace.
        
        This implementation performs:
        - Removal of whitespace between HTML tags (">  <" -> "><")
        - Reduction of excess whitespace after closing tags
        - Final trimming of leading and trailing whitespace

        Args:
            content: Raw HTML string to be minified.

        Returns:
            Minified HTML string.

        Note: 
            This is a lightweight minifier and doesn't perform
            structural validation or advanced HTML compression 🗜️.
        """
        content = re.sub(r">\s+<", "><", content)   # remove gaps between tags
        content = re.sub(r">\s+", " ", content)     # collapse whitespace
        return content.strip()                      # strip leading/trailing whitespace