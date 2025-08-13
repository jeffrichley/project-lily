"""Theme system for Lily CLI with Iris Bloom theme."""

from enum import Enum
from pathlib import Path
from typing import Any

from rich.theme import Theme
from prompt_toolkit.styles import Style


class ThemeName(str, Enum):
    """Available theme names."""

    IRIS_BLOOM = "iris-bloom"
    LIGHT = "light"
    DARK = "dark"


# Iris Bloom Theme - Purple-first theme for Lily CLI
IRIS_RICH_THEME = Theme(
    {
        "text": "#F7F7FA",
        "muted": "#B7B5C6",
        "prompt": "#9D66FF bold",
        "command": "#7C3AED bold",
        "flag": "#C0A8FF",
        "path": "#22D3EE",
        "rule.line": "#E0D6FF",
        "info": "#38BDF8",
        "success": "#34D399 bold",
        "warning": "#F59E0B bold",
        "error": "#EF4444 bold",
        "heading": "#5B2E91 bold",
        "pending": "#A78BFA",
        "background": "#1A1026",
        "panel": "#221433",
        "border": "#3A1F5C",
        "accent": "#5B2E91",
        "highlight": "#7C3AED",
        "secondary": "#9D66FF",
        "muted.accent": "#C0A8FF",
        "divider": "#E0D6FF",
        "light.bg": "#F3EFFF",
        "light.text": "#0E0E12",
        "light.muted": "#58546A",
    }
)

# Light theme variant
LIGHT_RICH_THEME = Theme(
    {
        "text": "#0E0E12",
        "muted": "#58546A",
        "prompt": "#7C3AED bold",
        "command": "#5B2E91 bold",
        "flag": "#3A1F5C",
        "path": "#22D3EE",
        "rule.line": "#E0D6FF",
        "info": "#38BDF8",
        "success": "#34D399 bold",
        "warning": "#F59E0B bold",
        "error": "#EF4444 bold",
        "heading": "#7C3AED bold",
        "pending": "#A78BFA",
        "background": "#F3EFFF",
        "panel": "#FFFFFF",
        "border": "#E0D6FF",
        "accent": "#7C3AED",
        "highlight": "#5B2E91",
        "secondary": "#3A1F5C",
        "muted.accent": "#58546A",
        "divider": "#C0A8FF",
    }
)

# Dark theme variant (simplified)
DARK_RICH_THEME = Theme(
    {
        "text": "#F7F7FA",
        "muted": "#B7B5C6",
        "prompt": "#9D66FF bold",
        "command": "#7C3AED bold",
        "flag": "#C0A8FF",
        "path": "#22D3EE",
        "rule.line": "#E0D6FF",
        "info": "#38BDF8",
        "success": "#34D399 bold",
        "warning": "#F59E0B bold",
        "error": "#EF4444 bold",
        "heading": "#5B2E91 bold",
        "pending": "#A78BFA",
        "background": "#0E0E12",
        "panel": "#1A1026",
        "border": "#221433",
        "accent": "#5B2E91",
        "highlight": "#7C3AED",
        "secondary": "#9D66FF",
        "muted.accent": "#C0A8FF",
        "divider": "#E0D6FF",
    }
)

# Prompt Toolkit styles for interactive shell
IRIS_PT_STYLE = Style.from_dict(
    {
        "prompt": "bold #9D66FF",
        "input": "#F7F7FA",
        "completion-menu.completion": "#C0A8FF",
        "completion-menu.completion.current": "bg:#C0A8FF #0E0E12",
        "scrollbar.background": "#221433",
        "scrollbar.button": "#9D66FF",
    }
)

LIGHT_PT_STYLE = Style.from_dict(
    {
        "prompt": "bold #7C3AED",
        "input": "#0E0E12",
        "completion-menu.completion": "#3A1F5C",
        "completion-menu.completion.current": "bg:#3A1F5C #F3EFFF",
        "scrollbar.background": "#E0D6FF",
        "scrollbar.button": "#7C3AED",
    }
)

DARK_PT_STYLE = Style.from_dict(
    {
        "prompt": "bold #9D66FF",
        "input": "#F7F7FA",
        "completion-menu.completion": "#C0A8FF",
        "completion-menu.completion.current": "bg:#C0A8FF #0E0E12",
        "scrollbar.background": "#1A1026",
        "scrollbar.button": "#9D66FF",
    }
)


class ThemeManager:
    """Manages theme switching and configuration."""

    def __init__(self, theme_name: ThemeName = ThemeName.IRIS_BLOOM):
        """Initialize theme manager with default theme."""
        self._theme_name = theme_name
        self._themes = {
            ThemeName.IRIS_BLOOM: (IRIS_RICH_THEME, IRIS_PT_STYLE),
            ThemeName.LIGHT: (LIGHT_RICH_THEME, LIGHT_PT_STYLE),
            ThemeName.DARK: (DARK_RICH_THEME, DARK_PT_STYLE),
        }

    @property
    def current_theme(self) -> ThemeName:
        """Get current theme name."""
        return self._theme_name

    @property
    def rich_theme(self) -> Theme:
        """Get current Rich theme."""
        return self._themes[self._theme_name][0]

    @property
    def pt_style(self) -> Style:
        """Get current Prompt Toolkit style."""
        return self._themes[self._theme_name][1]

    def switch_theme(self, theme_name: ThemeName) -> None:
        """Switch to a different theme."""
        if theme_name not in self._themes:
            raise ValueError(f"Unknown theme: {theme_name}")
        self._theme_name = theme_name

    def get_available_themes(self) -> list[ThemeName]:
        """Get list of available themes."""
        return list(self._themes.keys())

    def load_theme_from_config(self, config_path: Path) -> None:
        """Load theme from configuration file."""
        # This will be implemented when we add theme persistence
        pass

    def save_theme_to_config(self, config_path: Path) -> None:
        """Save current theme to configuration file."""
        # This will be implemented when we add theme persistence
        pass


# Global theme manager instance
theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    return theme_manager


def switch_theme(theme_name: ThemeName) -> None:
    """Switch the global theme."""
    theme_manager.switch_theme(theme_name)
