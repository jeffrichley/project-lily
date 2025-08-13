"""Lily CLI package."""

from pathlib import Path

from rich.console import Console

from lily.cli.commands.config import config
from lily.cli.commands.run import run
from lily.cli.commands.start import start
from lily.cli.commands.version import version
from lily.cli.main import app, main
from lily.cli.utils import get_console, show_banner
from lily.config import ConfigManager
from lily.shell import ShellManager
from lily.theme import get_theme_manager

# Export commonly used objects for testing
console = get_console()
theme_manager = get_theme_manager()

__all__ = [
    "app",
    "main",
    "show_banner",
    "start",
    "run",
    "config",
    "version",
    "ConfigManager",
    "ShellManager",
    "console",
    "theme_manager",
    "Path",
    "Console",
]
