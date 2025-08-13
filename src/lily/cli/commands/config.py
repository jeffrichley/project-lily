"""Config command for Lily CLI."""

from pathlib import Path

import typer

from lily.cli.utils import get_console, show_banner
from lily.config import ConfigManager
from lily.theme import ThemeName, get_theme_manager

# Initialize theme manager
theme_manager = get_theme_manager()


def config(
    show: bool = typer.Option(
        False,
        "--show",
        "-s",
        help="Show current configuration",
    ),
    set_theme: str | None = typer.Option(
        None,
        "--theme",
        "-t",
        help="Set theme (iris-bloom, light, dark)",
    ),
    config_file: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """Manage Lily configuration."""
    try:
        show_banner()

        config_manager = ConfigManager(config_file)
        lily_config = config_manager.load_config()

        # Update global theme manager with config theme
        theme_manager.switch_theme(lily_config.theme)

        if set_theme:
            try:
                theme_enum = ThemeName(set_theme)
                config_manager.update_config(theme=theme_enum)
                get_console().print(f"[success]Theme set to: {set_theme}[/success]")
            except ValueError:
                available = ", ".join(
                    [t.value for t in theme_manager.get_available_themes()]
                )
                get_console().print(f"[error]Unknown theme: {set_theme}[/error]")
                get_console().print(f"[text]Available themes: {available}[/text]")
                raise typer.Exit(1) from None

        if show or not set_theme:
            config_manager.show_config(lily_config)

    except Exception as e:
        get_console().print(f"[error]Configuration management failed: {e}[/error]")
        raise typer.Exit(1) from e
