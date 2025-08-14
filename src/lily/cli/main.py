"""Main CLI entry point for Lily."""

import sys
from pathlib import Path

import typer

from lily.cli.commands import compose, config, run, start, version
from lily.cli.utils import get_console
from lily.compose.engine import CompositionEngine

# Create Typer app
app = typer.Typer(
    name="lily",
    help="🌙 Lily - Software development project planning and organization tool",
    add_completion=False,
    rich_markup_mode="rich",
)

# Add commands from commands directory
app.command()(start.start)
app.command()(run.run)
app.command()(config.config)
app.command()(version.version)
app.command()(compose.compose)


@app.command()
def info(
    file: Path = typer.Argument(..., help="Petal file to inspect"),
) -> None:
    """Show information about a Petal workflow."""
    try:
        if file is None:
            typer.echo("Please provide a Petal file to inspect", err=True)
            typer.echo("Usage: lily info <file>", err=True)
            sys.exit(1)

        # Show composition information
        engine = CompositionEngine()
        composition_info = engine.get_composition_info(file)

        print("Petal Information:")
        print(f"Name: {composition_info['petal']['name']}")
        print(f"Description: {composition_info['petal']['description']}")
        print(f"Extends: {composition_info['petal']['extends']}")
        print(
            f"Composition enabled: {composition_info['petal']['composition_enabled']}"
        )
        print(f"Parameters: {composition_info['petal']['parameters']}")
        print(
            f"Environment variables: {composition_info['petal']['environment_variables']}"
        )
        print(f"Variables: {composition_info['petal']['variables']}")
        print(f"Steps: {composition_info['petal']['steps']}")

        print("\nComposition Status:")
        print(f"Valid: {composition_info['composition']['valid']}")
        if not composition_info["composition"]["valid"]:
            print(f"Errors: {composition_info['composition']['errors']}")

    except Exception as e:
        typer.echo(f"Error getting Petal workflow info: {e}", err=True)
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    try:
        app()
    except Exception as e:
        get_console().print(f"[error]Unexpected error: {e}[/error]")
        sys.exit(1)


if __name__ == "__main__":
    main()
