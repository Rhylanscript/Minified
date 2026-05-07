# minifiers/base.py

"""
Base interface for all file minifiers.

Defines the abstract structure that all child minifiers will follow
when inheriting from the parent class, ensuring a consistent API for
processing different file types.
"""

from abc import ABC, abstractmethod

class BaseMinifier(ABC):
    """
    Abstract base class for all minifier implementations.

    Each minifier defines which which file type it supports and implements
    the logic it needs to minify file content in the `minify()` method.

    Subclasses must:
    - Specify supported filetypes in `file_types`
    - Implement the `minify()` method
    """

    file_types: list[str] = []
    """
    List of supported file extensions for this minifier.\n
    Note that list entries *MUST* have a leading dot. 

    Example:
        [".html", ".htm"]
    """

    @abstractmethod
    def minify(self, content: str) -> str: 
        """
        Minifies the given file contents.

        Args:
            content: Raw string content of the file to minify.

        Returns:
            Minified version of the input as a string.

        Raises:
            Exception: Any implementation-specific errors 
                may be raised if the content is invalid or unsupported.
        """
        ...