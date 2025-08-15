"""Compose command for Lily Petal CLI."""

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import typer

from lily.compose.engine import CompositionEngine

if TYPE_CHECKING:
    from lily.petal.models import Petal

app = typer.Typer(help="Compose Petal workflows")


def _print_petal_info(composition_info: dict[str, dict[str, object]]) -> None:
    """Print petal information."""
    print("Petal Information:")
    print(f"Name: {composition_info['petal']['name']}")
    print(f"Description: {composition_info['petal']['description']}")
    print(f"Extends: {composition_info['petal']['extends']}")
    print(f"Composition enabled: {composition_info['petal']['composition_enabled']}")
    print(f"Parameters: {composition_info['petal']['parameters']}")
    print(
        f"Environment variables: {composition_info['petal']['environment_variables']}"
    )
    print(f"Variables: {composition_info['petal']['variables']}")
    print(f"Steps: {composition_info['petal']['steps']}")


def _print_composition_info(composition_info: dict[str, dict[str, object]]) -> None:
    """Print composition information."""
    print("Composition Information:")
    print(f"Valid: {composition_info['composition']['valid']}")
    if not composition_info["composition"]["valid"]:
        print(f"Errors: {composition_info['composition']['errors']}")


def _print_dry_run_info(composed_petal: "Petal") -> None:
    """Print dry run information."""
    print("Composed Petal Configuration (dry run):")
    print(f"Name: {composed_petal.name}")
    print(f"Description: {composed_petal.description}")
    print(f"Parameters: {len(composed_petal.params)}")
    print(f"Environment variables: {len(composed_petal.env)}")
    print(f"Variables: {len(composed_petal.vars)}")
    print(f"Steps: {len(composed_petal.steps)}")

    if composed_petal.params:
        print("\nParameters:")
        for name, param in composed_petal.params.items():
            print(f"  {name}: {param.type} = {param.default!r}")

    if composed_petal.env:
        print("\nEnvironment Variables:")
        for name, value in composed_petal.env.items():
            print(f"  {name}: {value}")


def _handle_info_command(
    composition_info: dict[str, dict[str, object]], info_type: str
) -> None:
    """Handle the info command with different types."""
    if info_type == "petal":
        _print_petal_info(composition_info)
    elif info_type == "composition":
        _print_composition_info(composition_info)
    else:
        # Show all info
        print("Full Composition Information:")
        print(json.dumps(composition_info, indent=2))


@app.command()
def compose(
    petal_file: Path = typer.Argument(..., help="Path to Petal workflow file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be executed"
    ),
    info: str | None = typer.Option(
        None, "--info", "-i", help="Show info: petal, composition, all"
    ),
) -> None:
    """Compose a Petal workflow."""
    engine = CompositionEngine()

    try:
        if info:
            # Show composition information
            composition_info = engine.get_composition_info(petal_file)
            _handle_info_command(composition_info, info)
            return

        # Single composition
        composed_petal = engine.compose_petal(petal_file)

        if dry_run:
            _print_dry_run_info(composed_petal)
        else:
            print(f"Composed Petal workflow: {composed_petal.name}")
            print(f"Parameters: {len(composed_petal.params)}")
            print(f"Environment variables: {len(composed_petal.env)}")
            print(f"Steps: {len(composed_petal.steps)}")
            # Here you would execute the workflow

    except Exception as e:
        typer.echo(f"Error composing Petal workflow: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    app()
