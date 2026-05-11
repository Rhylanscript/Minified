# minifiers/svg_minifier.py

"""
SVG minifier implementation.

Performs SVG-specific optimisations in addition to 
generic XML minification.
"""

import re
import xml.etree.ElementTree as ET

from typing import override
from minifiers.xml_minifier import XMLMinifier

class SVGMinifier(XMLMinifier):
    """
    Minifier for SVG files.

    Supports:
    - .svg

    Optimisations:
    - removes comments
    - removes metadata tags
    - removes editor specific tags
    - collapses unnecessary whitespace
    """

    file_types = [".svg"]

    @override
    def minify(self, content: str) -> str:
        """
        Minifies SVG content.

        Args:
            content: Raw SVG string

        Returns:
            Minified SVG string

        Raises:
            xml.etree.ElementTree.ParseError:
                If SVG/XML is invalid
        """
        # helper method to clean svg tags
        def clean_tag(tag: str) -> str:
            """
            Sometimes namespace tags like:
            `{http://www.w3.org/2000/svg}svg`
            are encountered, which happens with `ElementTree`.
            This helper removes the unnecessary content to parse
            correctly in the minifier.

            Args:
                tag: XML tag

            Returns:
                The cleaned tag.
            """
            return tag.split("}")[-1].lower()

        # remove xml comments and parse svg
        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        root = ET.fromstring(content)

        # remove metadata tags
        for elem in list(root):
            tag = clean_tag(elem.tag)
            if "metadata" in tag or "namedview" in tag: root.remove(elem)

        # serialise and collapse unecessary whitespace
        svg = ET.tostring(root, encoding="unicode")
        svg = re.sub(r">\s+<", "><", svg)
        svg = re.sub(r"\s{2,}", " ", svg)

        # return compacted svg string
        return svg.strip()