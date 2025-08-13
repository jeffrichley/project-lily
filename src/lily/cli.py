"""Main CLI entry point for Lily."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lily import __version__
from lily.config import ConfigManager
from lily.shell import ShellManager
from lily.theme import ThemeName, get_theme_manager

# Create Typer app
app = typer.Typer(
    name="lily",
    help="🌙 Lily - Software development project planning and organization tool",
    add_completion=False,
    rich_markup_mode="rich",
)

# Get theme manager and console
theme_manager = get_theme_manager()
console = Console(theme=theme_manager.rich_theme)


def show_banner() -> None:
    """Show the Lily banner."""
    # Ensure console is available
    global console
    if "console" not in globals() or console is None:
        console = Console(theme=theme_manager.rich_theme)

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


@app.command()
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
                console = Console(theme=theme_manager.rich_theme)
                console.print(f"[success]Using theme: {theme}[/success]")
            except ValueError:
                available = ", ".join(
                    [t.value for t in theme_manager.get_available_themes()]
                )
                console.print(f"[error]Unknown theme: {theme}[/error]")
                console.print(f"[text]Available themes: {available}[/text]")
                raise typer.Exit(1)

        # Validate configuration
        if not config_manager.validate_config(lily_config):
            console.print("[error]Configuration validation failed[/error]")
            raise typer.Exit(1)

        # Start shell
        shell_manager = ShellManager(lily_config)
        shell_manager.start_shell()

    except KeyboardInterrupt:
        console.print("\n[info]Goodbye![/info]")
        raise typer.Exit(0)
    except Exception as e:
        # Create console if it doesn't exist due to early error
        if "console" not in locals():
            console = Console(theme=theme_manager.rich_theme)
        console.print(f"[error]Failed to start shell: {e}[/error]")
        raise typer.Exit(1)


@app.command()
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
            console.print("[error]File must have .petal extension[/error]")
            raise typer.Exit(1)

        # Load configuration
        config_manager = ConfigManager(config)
        lily_config = config_manager.load_config()

        # Validate configuration
        if not config_manager.validate_config(lily_config):
            console.print("[error]Configuration validation failed[/error]")
            raise typer.Exit(1)

        console.print(f"[info]Running petal file: {file}[/info]")
        console.print("[warning]Petal execution not yet implemented[/warning]")

    except Exception as e:
        # Create console if it doesn't exist due to early error
        if "console" not in locals():
            console = Console(theme=theme_manager.rich_theme)
        console.print(f"[error]Failed to run petal file: {e}[/error]")
        raise typer.Exit(1)


@app.command()
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
    # Ensure console is available
    global console
    if "console" not in globals() or console is None:
        console = Console(theme=theme_manager.rich_theme)

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
                console.print(f"[success]Theme set to: {set_theme}[/success]")
            except ValueError:
                available = ", ".join(
                    [t.value for t in theme_manager.get_available_themes()]
                )
                console.print(f"[error]Unknown theme: {set_theme}[/error]")
                console.print(f"[text]Available themes: {available}[/text]")
                raise typer.Exit(1)

        if show or not set_theme:
            config_manager.show_config(lily_config)

    except Exception as e:
        # Create console if it doesn't exist due to early error
        if "console" not in locals():
            console = Console(theme=theme_manager.rich_theme)
        console.print(f"[error]Configuration management failed: {e}[/error]")
        raise typer.Exit(1)


@app.command()
def version() -> None:
    """Show Lily version."""
    show_banner()


def main() -> None:
    """Main entry point."""
    try:
        app()
    except Exception as e:
        console.print(f"[error]Unexpected error: {e}[/error]")
        sys.exit(1)


if __name__ == "__main__":
    main()
