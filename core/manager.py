# core/manager.py

"""
Handles file minification operations

This file has helper functions for minifying a file given a path,
which does so by passing it through the appropriate minifier, and
optionally writing it to an output file.
"""

import os

from core.registry import get_minifier

def minify_file(path: str) -> str | int:
    """
    Minifies the contents of a file by using the registered minifier.

    The correct minifier used to process the file's contents is 
    determined throught the file extension.

    Args:
        path: path to the input file.

    Returns:
        The minified file contents as a string.
        
        If no minifier matches the filetype, it will return 1.
    """

    # get the extension
    ext = os.path.splitext(path)[1]

    # get the minifier and quit with code 1 if no matching minifier found
    minifier = get_minifier(ext)
    if not minifier: return 1 
    # raise ValueError(f"No minifier for filetype \"{ext}\"")

    # open the file and read content, then minify and save to result to return
    with open(path, "r", encoding="utf-8") as f: content = f.read()
    result = minifier.minify(content)

    return result

def minify_file_to_output(path: str, output_path: str | None = None) -> str:
    """
    Minifies a file provided its path then writes the result to an
    output file at a specified path.

    If no output path is provided, a new file path is created by
    inserting `.min` before the file extension to signify the minified
    status.

    Args:
        path: The input file path.
        output_path: Optional output file path, defaults to None.

    Returns:
        The path to the written output file.


    """
    # fetch the minified file using minify
    result = minify_file(path)

    # write result to path (defaults to {path}.min.{extension})
    if not output_path: output_path = path.replace('.', ".min.")
    with open(output_path, "w", encoding="utf-8") as f: f.write(result)

    return output_path