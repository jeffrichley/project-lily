"""CLI utility functions for Lily."""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lily import __version__
from lily.theme import get_theme_manager


def get_console() -> Console:
    """Get a console instance with the current theme."""
    theme_manager = get_theme_manager()
    return Console(theme=theme_manager.rich_theme)


def show_banner() -> None:
    """Show the Lily banner."""
    console = get_console()

    banner_text = Text()
    banner_text.append("🌙 ", style="highlight")
    banner_text.append("Lily", style="heading")
    banner_text.append(" v", style="text")
    banner_text.append(__version__, style="command")
    banner_text.append("\n", style="text")
    banner_text.append(
        "Software development project planning and organization tool", style="muted"
    )

    banner_panel = Panel(banner_text, border_style="accent", padding=(1, 2))
    console.print(banner_panel)
