"""Start command for Lily CLI."""

from pathlib import Path

import typer

from lily.cli.utils import get_console, show_banner
from lily.config import ConfigManager
from lily.shell import ShellManager
from lily.theme import ThemeName, get_theme_manager

# Initialize theme manager
theme_manager = get_theme_manager()


def start(
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        dir_okay=False,
    ),
    theme: str | None = typer.Option(
        None,
        "--theme",
        "-t",
        help="Theme to use (iris-bloom, light, dark)",
    ),
) -> None:
    """Start the Lily interactive shell."""
    try:
        show_banner()

        # Load configuration
        config_manager = ConfigManager(config)
        lily_config = config_manager.load_config()

        # Apply theme if specified
        if theme:
            try:
                theme_enum = ThemeName(theme)
                theme_manager.switch_theme(theme_enum)
                # Update console with new theme
                get_console().print(f"[success]Using theme: {theme}[/success]")
            except ValueError:
                available = ", ".join(
                    [t.value for t in theme_manager.get_available_themes()]
                )
                get_console().print(f"[error]Unknown theme: {theme}[/error]")
                get_console().print(f"[text]Available themes: {available}[/text]")
                raise typer.Exit(1) from None

        # Validate configuration
        if not config_manager.validate_config(lily_config):
            get_console().print("[error]Configuration validation failed[/error]")
            raise typer.Exit(1)

        # Start shell
        shell_manager = ShellManager(lily_config)
        shell_manager.start_shell()

    except KeyboardInterrupt:
        get_console().print("\n[info]Goodbye![/info]")
        raise typer.Exit(0) from None
    except Exception as e:
        get_console().print(f"[error]Failed to start shell: {e}[/error]")
        raise typer.Exit(1) from e
