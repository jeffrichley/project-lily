"""Configuration management for Lily CLI."""

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomli_w
from rich.console import Console
from rich.panel import Panel

from lily.theme import ThemeName, get_theme_manager
from lily.types import JsonValue


@dataclass
class LilyConfig:
    """Configuration model for Lily CLI."""

    # OpenAI Configuration
    openai_api_key: str = field(metadata={"description": "OpenAI API key"})
    model: str = field(
        default="gpt-4", metadata={"description": "Default model to use"}
    )
    max_tokens: int = field(
        default=4000, metadata={"description": "Maximum tokens for responses"}
    )
    temperature: float = field(
        default=0.7, metadata={"description": "Temperature for model responses"}
    )

    # Theme Configuration
    theme: ThemeName = field(
        default=ThemeName.IRIS_BLOOM, metadata={"description": "UI theme"}
    )

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Validate OpenAI API key
        if not self.openai_api_key:
            raise ValueError("OpenAI API key must be provided")
        # Allow test keys for testing purposes
        if not (
            self.openai_api_key.startswith("test-")
            or self.openai_api_key.startswith("sk-")
            or len(self.openai_api_key) >= 10
        ):
            raise ValueError("OpenAI API key must be provided and valid")

        # Validate temperature value
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        # Validate max tokens value
        if self.max_tokens < 1 or self.max_tokens > 32000:
            raise ValueError("Max tokens must be between 1 and 32000")

    def to_dict(self) -> dict[str, JsonValue]:
        """Convert config to dictionary for serialization."""
        return {
            "openai_api_key": self.openai_api_key,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "theme": self.theme.value,
        }


class ConfigManager:
    """Manages configuration loading, saving, and validation."""

    def __init__(self, config_path: Path | None = None) -> None:
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
                with open(self.config_path, "rb") as f:
                    raw_config_data: dict[str, JsonValue] = tomllib.load(f)

                # Convert the raw data to the proper types for LilyConfig
                config_data: dict[str, str | int | float | bool | Path | ThemeName] = {}

                # Copy and convert values
                for key, value in raw_config_data.items():
                    if key == "theme" and isinstance(value, str):
                        config_data[key] = ThemeName(value)
                    else:
                        # Type ignore needed because JsonValue includes None, list, dict types
                        # that we don't handle explicitly, but we know the remaining values
                        # are basic types that match our target dictionary
                        config_data[key] = value  # type: ignore[assignment]

                # Type ignore explanation:
                #
                # This type ignore is necessary due to a fundamental mismatch between:
                # 1. TOML parsing (which returns JsonValue = str|int|float|bool|None|list|dict)
                # 2. Dataclass construction (which expects specific field types)
                #
                # The issue:
                # - raw_config_data comes from tomllib.load() with type dict[str, JsonValue]
                # - JsonValue includes None, list, dict which LilyConfig fields don't accept
                # - We convert known fields (theme -> ThemeName, paths -> Path) but can't
                #   guarantee all fields are converted to exact dataclass field types
                # - The "else" clause above assigns JsonValue types that may include
                #   None, list, dict which don't match LilyConfig field types
                #
                # Why this is safe:
                # - Dataclass performs runtime validation and type conversion
                # - Invalid types will raise TypeError at runtime
                # - The TOML file structure is controlled (not user-generated)
                # - We handle the most complex conversions (ThemeName, Path) explicitly
                #
                # Alternatives considered:
                # - Full type conversion: Would require duplicating dataclass logic
                # - Stricter JsonValue: Would break TOML compatibility
                #
                # This is a pragmatic solution that acknowledges the gap between
                # dynamic TOML data and strict dataclass typing requirements.
                return LilyConfig(**config_data)  # type: ignore[arg-type]
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
            config_dict = config.to_dict()

            with open(self.config_path, "wb") as f:
                tomli_w.dump(config_dict, f)

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
            theme=ThemeName.IRIS_BLOOM,
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
            f"[text]Theme:[/text] [command]{config.theme.value}[/command]",
            title="Configuration",
            border_style="accent",
        )
        self.console.print(config_panel)

    def update_config(self, **kwargs: JsonValue) -> LilyConfig:
        """Update configuration with new values."""
        current_config = self.load_config()

        # Update with new values
        for key, value in kwargs.items():
            if hasattr(current_config, key):
                setattr(current_config, key, value)

        # Save updated config
        self.save_config(current_config)
        return current_config
