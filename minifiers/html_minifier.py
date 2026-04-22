# minifiers/html_minifier.py

import re

from typing import override

from minifiers.base import BaseMinifier

class HTMLMinifier(BaseMinifier):
    file_types = [".html"]

    @override
    def minify(self, content: str) -> str:
        content = re.sub(r">\s+<", "><", content)   # remove gaps between tags
        content = re.sub(r">\s+", " ", content)     # collapse whitespace
        return content.strip()

    