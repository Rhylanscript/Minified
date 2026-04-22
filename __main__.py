# __main__.py

"""
To run use the command below in a terminal:

    python __main__.py test.json

"""

import sys

from core.manager import minify_file

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print("Usage: python __main__.py <file>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        result = minify_file(path)
        print(result)

    except Exception as e:
        print(f"Error: {e}")