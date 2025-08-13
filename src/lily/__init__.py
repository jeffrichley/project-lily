"""Project Lily - Software development project planning and organization tool."""

__version__ = "0.1.0"
__author__ = "Jeff Richley"
__email__ = "jeffrichley@gmail.com"

from lily.config import LilyConfig
from lily.shell import ShellManager
from lily.theme import IRIS_RICH_THEME

__all__ = [
    "LilyConfig",
    "ShellManager",
    "IRIS_RICH_THEME",
    "__version__",
    "__author__",
    "__email__",
]
