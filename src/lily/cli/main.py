"""Main CLI entry point for Lily."""

import sys

import typer

from lily.cli.commands import config, run, start, version
from lily.cli.utils import get_console

# Create Typer app
app = typer.Typer(
    name="lily",
    help="🌙 Lily - Software development project planning and organization tool",
    add_completion=False,
    rich_markup_mode="rich",
)

# Add commands directly
app.command()(start.start)
app.command()(run.run)
app.command()(config.config)
app.command()(version.version)


def main() -> None:
    """Main entry point."""
    try:
        app()
    except Exception as e:
        get_console().print(f"[error]Unexpected error: {e}[/error]")
        sys.exit(1)


if __name__ == "__main__":
    main()
