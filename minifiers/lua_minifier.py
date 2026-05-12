# minifiers/lua_minifier.py

"""
Lua minifier implementation.

Minifies Lua source code by:
- Removing comments
- Collapsing unnecessary whitespace
- Preserving strings and valid syntax

Supports:
- Single-line comments (-- ...)
- Multi-line comments (--[[ ... ]])

This implementation uses a character scanner / state machine
approach instead of regex only replacements to safely preserve
Lua syntax.
"""

from typing import override

from minifiers.base import BaseMinifier

class LuaMinifier(BaseMinifier):
    """
    Minifier for Lua source files.

    Supports:
    - .lua

    Removes:
    - Comments
    - Extra whitespace
    - Blank lines

    Preserves:
    - Strings
    - Required spacing between identifiers
    """

    file_types = [".lua"]

    @override
    def minify(self, content: str) -> str:
        """
        Minifies Lua source code.

        Args:
            content: Raw Lua source code

        Returns:
            Minified Lua source code
        """

        result = []

        i = 0
        length = len(content)

        in_string = False
        string_char = None
        prev_char = ""

        while i < length:
            ch = content[i]

            # handle string
            if in_string:
                result.append(ch)

                # escaped char
                if ch == '\\' and i + 1 < length:
                    result.append(content[i+1])
                    i += 2
                    continue

                # end of string
                if ch == string_char:
                    in_string = False
                    string_char = None

                i += 1
                prev_char = ch
                continue

            # start string
            if ch in ('"', '\''):
                in_string = True
                string_char = ch

                result.append(ch)

                i += 1
                prev_char = ch
                continue

            # multi line comments
            if content[i:i+4] == "--[[":
                end = content.find("]]", i+4)

                # unclosed comment : skip rest
                if end == -1: break

                i = end + 2
                continue

            # single line comments
            if content[i:i+2] == "--":
                newline = content.find("\n", i)

                # comment until eof
                if newline == -1: break

                i = newline
                result.append('\n')
                continue

            # whitespace collapsing
            if ch.isspace():

                next_char = ""
                j = i + 1

                while j < length:
                    if not content[j].isspace():
                        next_char = content[j]
                        break
                    j += 1

                # keep one space if needed
                if self.is_identifier_char(prev_char) and self.is_identifier_char(next_char):
                    result.append(" ")
                    prev_char = " "

                i += 1
                continue

            # normal char
            result.append(ch)
            prev_char = ch

            i += 1

        return "".join(result).strip()
    
    def is_identifier_char(ch: str) -> bool:
        return ch.isalnum() or ch == '_'