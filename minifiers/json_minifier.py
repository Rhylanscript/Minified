# minifiers/json_minifier.py

"""
JSON minifier implementation.

Converts JSON content into a much more compact form by removing
all unnecessary whitespace while preserving valid structure.
"""

import json

from typing import override
from minifiers.base import BaseMinifier

class JSONMinifier(BaseMinifier):
    """
    Minifier for JSON files.

    Supports:
    - .json

    Converts formatted JSON into a compacted string version by 
    removing all whitespace between elements while preserving
    valid JSON structure.
    """
    file_types = [".json"]

    @override
    def minify(self, content: str) -> str:
        """
        Minifies JSON content by removing unecessary whitespace.

        The process works by:
        - Parsing the input JSON string into a python object
        - Remaking it using compact separators

        Args:
            content: Raw JSON string

        Returns:
            A compacted JSON string with no unecessary whitespace.

        Raises:
            json.JSONDecodeError: If input is not a valid JSON
        """
        return json.dumps(json.loads(content), separators=(",", ":"))