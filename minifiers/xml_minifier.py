# minifiers/xml_minifier.py

"""
XML Minifier implementation.

Minifies XML files by removing unecessary whitespace between
elements while preserving valid XML structure.
"""

import re
import xml.etree.ElementTree as ET

from typing import override
from minifiers.base import BaseMinifier

class XMLMinifier(BaseMinifier):
    """
    Minifier for XML files.

    Supports:
    - .xml

    Performs safe structural minification by:
    - Parsing XML
    - Reserialising without formatting
    - Collapsing inner tag whitespace
    """

    file_types = [".xml"]

    @override
    def minify(self, content: str) -> str:
        """
        Minifies XML content safely.

        Args:
            content: Raw XML string

        Returns:
            Compacted XML string

        Raises:
            xml.etree.ElementTree.ParseError:
                If XML is invalid
        """
        # parse xml
        root = ET.fromstring(content)

        # serialise back into compact form and remove whitespace between tags
        xml = ET.tostring(root, encoding="unicode")
        xml = re.sub(r">\s+<", "><", xml)

        # return minified string
        return xml.strip()