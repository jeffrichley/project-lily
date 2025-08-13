"""Run command for Lily CLI."""

from pathlib import Path

import typer

from lily.cli.utils import get_console, show_banner
from lily.config import ConfigManager


def run(
    file: Path = typer.Argument(
        ...,
        help="Path to .petal file to execute",
        exists=True,
        dir_okay=False,
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        dir_okay=False,
    ),
) -> None:
    """Run a .petal file directly."""
    try:
        show_banner()

        if file.suffix != ".petal":
            get_console().print("[error]File must have .petal extension[/error]")
            raise typer.Exit(1)

        # Load configuration
        config_manager = ConfigManager(config)
        lily_config = config_manager.load_config()

        # Validate configuration
        if not config_manager.validate_config(lily_config):
            get_console().print("[error]Configuration validation failed[/error]")
            raise typer.Exit(1)

        get_console().print(f"[info]Running petal file: {file}[/info]")
        get_console().print("[warning]Petal execution not yet implemented[/warning]")

    except Exception as e:
        get_console().print(f"[error]Failed to run petal file: {e}[/error]")
        raise typer.Exit(1) from e
