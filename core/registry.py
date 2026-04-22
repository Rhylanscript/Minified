# core/registry.py

from minifiers import *

MINIFIERS = [
    JSONMinifier(),
    HTMLMinifier(),
]

def get_minifier(file_extension: str) -> BaseMinifier | None: 
    return next((m for m in MINIFIERS if file_extension.lower() in m.file_types), None)