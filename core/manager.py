# core/manager.py

import os

from core.registry import get_minifier

def minify_file(path: str) -> str | int:
    ext = os.path.splitext(path)[1]

    minifier = get_minifier(ext)
    if not minifier: return 1 #raise ValueError(f"No minifier for filetype \"{ext}\"")

    with open(path, "r", encoding="utf-8") as f: content = f.read()
    result = minifier.minify(content)

    return result

def minify_file_to_output(path: str, output_path: str | None = None) -> str:
    result = minify_file(path)

    if not output_path: output_path = path.replace('.', ".min.")
    with open(output_path, "w", encoding="utf-8") as f: f.write(result)

    return output_path