"""Interactive shell for Lily CLI."""

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lily.config import LilyConfig
from lily.theme import get_theme_manager


@dataclass
class Message:
    """Represents a message in the conversation."""

    role: str
    content: str
    timestamp: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Command:
    """Represents a command that can be executed."""

    name: str
    description: str
    handler: Callable[[List[str]], str]
    aliases: List[str] = field(default_factory=list)


@dataclass
class ShellState:
    """State of the interactive shell."""

    config: LilyConfig
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_history: List[Message] = field(default_factory=list)
    available_commands: Dict[str, Command] = field(default_factory=dict)
    is_running: bool = True
    current_directory: Path = field(default_factory=Path.cwd)


class ShellManager:
    """Manages the interactive shell session."""

    def __init__(self, config: LilyConfig):
        """Initialize shell manager."""
        self.config = config
        self.state = ShellState(config=config)
        self.theme_manager = get_theme_manager()
        self.console = Console(theme=self.theme_manager.rich_theme)

        # Set up prompt session
        history_file = self.config.sessions_dir / f"history_{self.state.session_id}.txt"
        history_file.parent.mkdir(parents=True, exist_ok=True)

        self.prompt_session = PromptSession(
            history=FileHistory(str(history_file)),
            style=self.theme_manager.pt_style,
        )

        # Initialize built-in commands
        self._setup_commands()

        # Set up auto-completion
        if self.config.auto_complete:
            self.completer = WordCompleter(
                list(self.state.available_commands.keys()), ignore_case=True
            )
        else:
            self.completer = None

    def _setup_commands(self) -> None:
        """Set up built-in commands."""
        self.register_command(
            Command(
                name="help",
                description="Show available commands",
                handler=self._cmd_help,
                aliases=["h", "?"],
            )
        )

        self.register_command(
            Command(
                name="exit",
                description="Exit the shell",
                handler=self._cmd_exit,
                aliases=["quit", "q"],
            )
        )

        self.register_command(
            Command(
                name="clear",
                description="Clear the screen",
                handler=self._cmd_clear,
                aliases=["cls"],
            )
        )

        self.register_command(
            Command(
                name="config",
                description="Show current configuration",
                handler=self._cmd_config,
                aliases=["cfg"],
            )
        )

        self.register_command(
            Command(
                name="theme",
                description="Switch theme",
                handler=self._cmd_theme,
                aliases=["t"],
            )
        )

        self.register_command(
            Command(
                name="pwd",
                description="Show current working directory",
                handler=self._cmd_pwd,
            )
        )

        self.register_command(
            Command(name="cd", description="Change directory", handler=self._cmd_cd)
        )

        self.register_command(
            Command(
                name="ls",
                description="List directory contents",
                handler=self._cmd_ls,
                aliases=["dir"],
            )
        )

    def register_command(self, command: Command) -> None:
        """Register a new command."""
        self.state.available_commands[command.name] = command
        for alias in command.aliases:
            self.state.available_commands[alias] = command

    def start_shell(self) -> None:
        """Start the interactive shell."""
        self._show_welcome()

        while self.state.is_running:
            try:
                # Get user input
                user_input = self.prompt_session.prompt(
                    [("class:prompt", "lily > ")], completer=self.completer
                )

                if not user_input.strip():
                    continue

                # Process input
                result = self.process_input(user_input)
                if result:
                    self.console.print(result)

            except KeyboardInterrupt:
                self.console.print("\n[warning]Use 'exit' to quit[/warning]")
            except EOFError:
                self.console.print("\n[info]Goodbye![/info]")
                break
            except Exception as e:
                self.console.print(f"[error]Error: {e}[/error]")

    def process_input(self, input_text: str) -> str:
        """Process user input and return response."""
        # Parse command and arguments
        parts = input_text.strip().split()
        if not parts:
            return ""

        command_name = parts[0].lower()
        args = parts[1:]

        # Check if it's a built-in command
        if command_name in self.state.available_commands:
            command = self.state.available_commands[command_name]
            try:
                return command.handler(args)
            except Exception as e:
                return f"[error]Command '{command_name}' failed: {e}[/error]"

        # Check if it's a file path (for future .petal file execution)
        if Path(command_name).exists() and command_name.endswith(".petal"):
            return f"[info]Petals not implemented yet: {command_name}[/info]"

        # Unknown command
        return f"[error]Unknown command: {command_name}[/error]\n[text]Type 'help' for available commands[/text]"

    def _show_welcome(self) -> None:
        """Show welcome message."""
        welcome_text = Text()
        welcome_text.append("🌙 ", style="highlight")
        welcome_text.append("Lily", style="heading")
        welcome_text.append(" — Interactive Shell", style="text")
        welcome_text.append("\n\n", style="text")
        welcome_text.append("Type ", style="text")
        welcome_text.append("help", style="command")
        welcome_text.append(" for available commands", style="text")

        welcome_panel = Panel(
            welcome_text, title="Welcome", border_style="accent", padding=(1, 2)
        )
        self.console.print(welcome_panel)
        self.console.print()

    # Built-in command handlers

    def _cmd_help(self, args: List[str]) -> str:
        """Handle help command."""
        if not args:
            # Show all commands
            help_text = "[heading]Available Commands:[/heading]\n\n"
            for name, command in self.state.available_commands.items():
                if name == command.name:  # Only show primary command names
                    help_text += f"[command]{name}[/command] - {command.description}\n"
            return help_text
        else:
            # Show help for specific command
            command_name = args[0].lower()
            if command_name in self.state.available_commands:
                command = self.state.available_commands[command_name]
                return f"[command]{command.name}[/command] - {command.description}"
            else:
                return f"[error]Unknown command: {command_name}[/error]"

    def _cmd_exit(self, args: List[str]) -> str:
        """Handle exit command."""
        self.state.is_running = False
        return "[info]Goodbye![/info]"

    def _cmd_clear(self, args: List[str]) -> str:
        """Handle clear command."""
        self.console.clear()
        return ""

    def _cmd_config(self, args: List[str]) -> str:
        """Handle config command."""
        from lily.config import ConfigManager

        config_manager = ConfigManager()
        config_manager.show_config(self.config)
        return ""

    def _cmd_theme(self, args: List[str]) -> str:
        """Handle theme command."""
        if not args:
            # Show current theme
            return f"[text]Current theme:[/text] [command]{self.theme_manager.current_theme.value}[/command]"

        theme_name = args[0].lower()
        try:
            from lily.theme import ThemeName

            theme_enum = ThemeName(theme_name)
            self.theme_manager.switch_theme(theme_enum)
            # Update console theme
            self.console = Console(theme=self.theme_manager.rich_theme)
            return f"[success]Switched to theme: {theme_name}[/success]"
        except ValueError:
            available = ", ".join(
                [t.value for t in self.theme_manager.get_available_themes()]
            )
            return f"[error]Unknown theme: {theme_name}[/error]\n[text]Available themes: {available}[/text]"

    def _cmd_pwd(self, args: List[str]) -> str:
        """Handle pwd command."""
        return f"[path]{self.state.current_directory}[/path]"

    def _cmd_cd(self, args: List[str]) -> str:
        """Handle cd command."""
        if not args:
            return "[error]cd: missing directory argument[/error]"

        try:
            new_dir = Path(args[0])
            if new_dir.is_absolute():
                self.state.current_directory = new_dir
            else:
                self.state.current_directory = self.state.current_directory / new_dir

            self.state.current_directory = self.state.current_directory.resolve()
            return f"[success]Changed to: {self.state.current_directory}[/success]"
        except Exception as e:
            return f"[error]cd: {e}[/error]"

    def _cmd_ls(self, args: List[str]) -> str:
        """Handle ls command."""
        try:
            items = list(self.state.current_directory.iterdir())
            if not items:
                return "[muted]Directory is empty[/muted]"

            result = []
            for item in sorted(items):
                if item.is_dir():
                    result.append(f"[command]{item.name}/[/command]")
                else:
                    result.append(f"[text]{item.name}[/text]")

            return "  ".join(result)
        except Exception as e:
            return f"[error]ls: {e}[/error]"

    def exit_shell(self) -> None:
        """Exit the shell gracefully."""
        self.state.is_running = False
