# minifiers/base.py

from abc import ABC, abstractmethod

class BaseMinifier(ABC):
    file_types = []

    @abstractmethod
    def minify(self, content: str) -> str: ...