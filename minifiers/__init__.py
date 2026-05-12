# minifiers/__init__.py

"""
Minifier implementations package.

Provides a collection of file minifiers for different formats,
as well as an abstract parent `BaseMinifier which all minifiers 
inherit from.
"""

from .base import BaseMinifier

from .html_minifier import HTMLMinifier
from .json_minifier import JSONMinifier
from .css_minifier import CSSMinifier
from .xml_minifier import XMLMinifier
from .svg_minifier import SVGMinifier
from .js_minifier import JSMinifier
from .lua_minifier import LuaMinifier