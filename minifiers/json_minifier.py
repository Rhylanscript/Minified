# minifiers/json_minifier.py

import json

from typing import override
from minifiers.base import BaseMinifier

class JSONMinifier(BaseMinifier):
    file_types = [".json"]

    @override
    def minify(self, content: str) -> str:
        return json.dumps(json.loads(content), separators=(",", ":"))