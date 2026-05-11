# minifiers/js_minifier.py

"""
JavaScript minifier implementation.

Performs lightweight minification by:
- Removing single line and multi line comments
- Collapsing unnecessary whitespace
- Preserving code structure (no ast parsing)

Also has option of using an aggressive minifier
(requires esbuild to run)
"""

import re

from typing import override
from minifiers.base import BaseMinifier

class JSMinifier(BaseMinifier):
    """
    Minifier for JS files.

    Supports:
    - .js
    """

    file_types = [".js"]

    # regex minification cases to match
    
    # matches // comments but not urls and matches /* ... */ comments
    _single_line_comment = re.compile(r"(?<!:)//.*?$", flags = re.MULTILINE)
    _multi_line_comment = re.compile(r"/\*.*?\*/", flags = re.DOTALL)

    # collapses whitespace
    _multi_space = re.compile(r"\s+")

    @override
    def minify(self, content: str) -> str:
        """
        Minifies JavaScript content.

        Will use esbuild if user has it. Otherwise uses a more
        risky minification method which can sometimes cause
        issues.
        """
        return self.aminify(content) if self.has_esbuild else self.pminify(content)
        
    
    def aminify(self, content: str) -> str:
        """
        A more aggressive minification method for js.
        Requires esbuild as it is an AST based minfier.

        Requires:
            npm install -g esbuild
        """
        import tempfile
        import subprocess

        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as f:
            f.write(content)
            input_path = f.name

        try:
            # run esbuild minifier
            result = subprocess.run(
                [
                    "esbuild",
                    input_path,
                    "--minify",
                    "--log-level=error"
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            
            return result.stdout.strip()
        
        except subprocess.CalledProcessError as e:
            # return original as fallback
            return content
        
        finally:
            try:
                import os
                os.remove(input_path)
            except Exception:...

    def pminify(self, content: str) -> str:
        """
        Minifies JavaScript content using a more risky minification
        method (only use if user doesn't have esbuild).

        This is a regex based minifier (NOT AST SAFE) suitable for:
        - basic scripts
        - frontend JS
        - non obfuscated code

        WARNING:
        Does not fully handle edge cases like regex 
        literals inside code.
        """
        # remove comments and collapse whitespace
        content = self._multi_line_comment.sub("", content)
        content = self._single_line_comment.sub("", content)
        content = self._multi_space.sub(" ", content)

        # remove space around common JS symbols
        content = re.sub(r"\s*([{}();=,+\-*/<>?:])\s*", r"\1", content)

        # return minified content
        return content.strip()
    
    def has_esbuild() -> bool:
        """Simple helper to check if the use has esbuild installed."""
        try:
            import subprocess
            subprocess.run(
                ["esbuild", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False