"""Configuration management for Lily CLI."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import toml
from pydantic import BaseModel, Field, field_validator
from rich.console import Console
from rich.panel import Panel

from lily.theme import ThemeName, get_theme_manager


class LilyConfig(BaseModel):
    """Configuration model for Lily CLI."""

    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4", description="Default model to use")
    max_tokens: int = Field(default=4000, description="Maximum tokens for responses")
    temperature: float = Field(
        default=0.7, description="Temperature for model responses"
    )

    # Directory Configuration
    commands_dir: Path = Field(
        default=Path("~/.lily/commands"), description="Commands directory"
    )
    rules_dir: Path = Field(
        default=Path("~/.lily/rules"), description="Rules directory"
    )
    sessions_dir: Path = Field(
        default=Path("~/.lily/sessions"), description="Sessions directory"
    )

    # Theme Configuration
    theme: ThemeName = Field(default=ThemeName.IRIS_BLOOM, description="UI theme")

    # Shell Configuration
    history_size: int = Field(default=1000, description="Command history size")
    auto_complete: bool = Field(default=True, description="Enable auto-completion")

    @field_validator("openai_api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate OpenAI API key format."""
        if not v:
            raise ValueError("OpenAI API key must be provided")
        # Allow test keys for testing purposes
        if v.startswith("test-") or v.startswith("sk-") or len(v) >= 10:
            return v
        raise ValueError("OpenAI API key must be provided and valid")

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature value."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max tokens value."""
        if v < 1 or v > 32000:
            raise ValueError("Max tokens must be between 1 and 32000")
        return v

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        # Expand user paths
        self.commands_dir = Path(self.commands_dir).expanduser()
        self.rules_dir = Path(self.rules_dir).expanduser()
        self.sessions_dir = Path(self.sessions_dir).expanduser()


class ConfigManager:
    """Manages configuration loading, saving, and validation."""

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration manager."""
        if config_path is None:
            config_path = Path.home() / ".lily" / "config.toml"
        self.config_path = Path(config_path).expanduser()
        self.console = Console(theme=get_theme_manager().rich_theme)

    def load_config(self) -> LilyConfig:
        """Load configuration from file or create default."""
        try:
            if self.config_path.exists():
                self.console.print(
                    f"[info]Loading configuration from {self.config_path}[/info]"
                )
                config_data = toml.load(self.config_path)
                # Convert theme string to enum if present
                if "theme" in config_data and isinstance(config_data["theme"], str):
                    config_data["theme"] = ThemeName(config_data["theme"])
                return LilyConfig(**config_data)
            else:
                self.console.print(
                    "[warning]Configuration file not found, creating default[/warning]"
                )
                return self.create_default_config()
        except Exception as e:
            self.console.print(f"[error]Failed to load configuration: {e}[/error]")
            return self.create_default_config()

    def save_config(self, config: LilyConfig) -> None:
        """Save configuration to file."""
        try:
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict and save
            config_dict = config.model_dump()
            # Convert Path objects to strings for TOML serialization
            config_dict["commands_dir"] = str(config_dict["commands_dir"])
            config_dict["rules_dir"] = str(config_dict["rules_dir"])
            config_dict["sessions_dir"] = str(config_dict["sessions_dir"])
            config_dict["theme"] = config_dict["theme"].value

            with open(self.config_path, "w") as f:
                toml.dump(config_dict, f)

            self.console.print(
                f"[success]Configuration saved to {self.config_path}[/success]"
            )
        except Exception as e:
            self.console.print(f"[error]Failed to save configuration: {e}[/error]")
            raise

    def create_default_config(self) -> LilyConfig:
        """Create default configuration."""
        # Try to get API key from environment
        api_key = os.getenv("OPENAI_API_KEY", "")

        config = LilyConfig(
            openai_api_key=api_key,
            model="gpt-4",
            max_tokens=4000,
            temperature=0.7,
            commands_dir=Path("~/.lily/commands"),
            rules_dir=Path("~/.lily/rules"),
            sessions_dir=Path("~/.lily/sessions"),
            theme=ThemeName.IRIS_BLOOM,
            history_size=1000,
            auto_complete=True,
        )

        # Save default config
        self.save_config(config)
        return config

    def validate_config(self, config: LilyConfig) -> bool:
        """Validate configuration values."""
        try:
            # Check if API key is set
            if not config.openai_api_key:
                self.console.print("[error]OpenAI API key is required[/error]")
                return False

            # Check if directories can be created
            for dir_path in [
                config.commands_dir,
                config.rules_dir,
                config.sessions_dir,
            ]:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.console.print(
                        f"[error]Cannot create directory {dir_path}: {e}[/error]"
                    )
                    return False

            self.console.print("[success]Configuration validation passed[/success]")
            return True
        except Exception as e:
            self.console.print(f"[error]Configuration validation failed: {e}[/error]")
            return False

    def show_config(self, config: LilyConfig) -> None:
        """Display current configuration."""
        config_panel = Panel(
            f"[heading]Lily Configuration[/heading]\n\n"
            f"[text]Model:[/text] [command]{config.model}[/command]\n"
            f"[text]Max Tokens:[/text] [command]{config.max_tokens}[/command]\n"
            f"[text]Temperature:[/text] [command]{config.temperature}[/command]\n"
            f"[text]Theme:[/text] [command]{config.theme.value}[/command]\n"
            f"[text]Commands Dir:[/text] [path]{config.commands_dir}[/path]\n"
            f"[text]Rules Dir:[/text] [path]{config.rules_dir}[/path]\n"
            f"[text]Sessions Dir:[/text] [path]{config.sessions_dir}[/path]\n"
            f"[text]History Size:[/text] [command]{config.history_size}[/command]\n"
            f"[text]Auto Complete:[/text] [command]{config.auto_complete}[/command]",
            title="Configuration",
            border_style="accent",
        )
        self.console.print(config_panel)

    def update_config(self, **kwargs: Any) -> LilyConfig:
        """Update configuration with new values."""
        current_config = self.load_config()

        # Update with new values
        for key, value in kwargs.items():
            if hasattr(current_config, key):
                setattr(current_config, key, value)

        # Save updated config
        self.save_config(current_config)
        return current_config
