"""Start command for Lily CLI."""

from pathlib import Path

import typer

from lily.cli.utils import get_console, show_banner
from lily.config import ConfigManager, LilyConfig
from lily.shell import run_interactive_command
from lily.theme import ThemeName, get_theme_manager

# Initialize theme manager
theme_manager = get_theme_manager()


def _apply_theme(theme: str | None) -> None:
    """Apply theme if specified."""
    if not theme:
        return

    try:
        theme_enum = ThemeName(theme)
        theme_manager.switch_theme(theme_enum)
        get_console().print(f"[success]Using theme: {theme}[/success]")
    except ValueError:
        available = ", ".join([t.value for t in theme_manager.get_available_themes()])
        get_console().print(f"[error]Unknown theme: {theme}[/error]")
        get_console().print(f"[text]Available themes: {available}[/text]")
        raise typer.Exit(1) from None


def _show_help() -> None:
    """Show interactive shell help."""
    get_console().print("[text]Available commands:[/text]")
    get_console().print("[text]  help    - Show this help[/text]")
    get_console().print("[text]  exit    - Exit the shell[/text]")
    get_console().print("[text]  version - Show Lily version[/text]")
    get_console().print("[text]  config  - Show configuration[/text]")


def _handle_builtin_command(
    command: str, config_manager: ConfigManager, lily_config: LilyConfig
) -> bool:
    """Handle builtin commands. Returns True if command was handled."""
    if command.lower() in ["exit", "quit", "q"]:
        get_console().print("[info]Goodbye![/info]")
        return True

    if command.lower() == "help":
        _show_help()
        return True

    if command.lower() == "version":
        get_console().print("[info]Lily v1.0.0[/info]")
        return True

    if command.lower() == "config":
        config_manager.show_config(lily_config)
        return True

    return False


def _run_interactive_shell(
    config_manager: ConfigManager, lily_config: LilyConfig
) -> None:
    """Run the interactive shell loop."""
    get_console().print("[info]Starting Lily interactive shell...[/info]")
    get_console().print("[text]Type 'exit' to quit[/text]")

    while True:
        try:
            # Get user input
            command = input("lily > ").strip()

            if not command:
                continue

            # Handle builtin commands
            if _handle_builtin_command(command, config_manager, lily_config):
                if command.lower() in ["exit", "quit", "q"]:
                    break
                continue

            # Execute command
            get_console().print(f"[text]Executing: {command}[/text]")
            exit_code = run_interactive_command(command)

            if exit_code != 0:
                get_console().print(
                    f"[warning]Command exited with code: {exit_code}[/warning]"
                )

        except KeyboardInterrupt:
            get_console().print("\n[info]Use 'exit' to quit[/info]")
        except EOFError:
            get_console().print("\n[info]Goodbye![/info]")
            break
        except Exception as e:
            get_console().print(f"[error]Error: {e}[/error]")


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
        _apply_theme(theme)

        # Validate configuration
        if not config_manager.validate_config(lily_config):
            get_console().print("[error]Configuration validation failed[/error]")
            raise typer.Exit(1)

        # Start interactive shell
        _run_interactive_shell(config_manager, lily_config)

    except KeyboardInterrupt:
        get_console().print("\n[info]Goodbye![/info]")
        raise typer.Exit(0) from None
    except Exception as e:
        get_console().print(f"[error]Failed to start shell: {e}[/error]")
        raise typer.Exit(1) from e
