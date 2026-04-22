# core/manager.py

import os

from core.registry import get_minifier

def minify_file(path: str) -> str | None:
    ext = os.path.splitext(path)[1]

    minifier = get_minifier(ext)
    if not minifier: raise ValueError(f"No minifier for filetype \"{ext}\"")

    with open(path, "r", encoding="utf-8") as f: content = f.read()
    result = minifier.minify(content)

    return result