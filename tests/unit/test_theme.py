"""Unit tests for theme system."""

import pytest

from lily.theme import ThemeManager, ThemeName, get_theme_manager, switch_theme


@pytest.mark.unit
class TestThemeName:
    """Test ThemeName enum."""

    def test_theme_names(self) -> None:
        """Test that all expected theme names exist."""
        # Arrange - No setup needed for enum value checks

        # Act - Access enum values

        # Assert - Verify enum values match expected strings
        assert ThemeName.IRIS_BLOOM.value == "iris-bloom"
        assert ThemeName.LIGHT.value == "light"
        assert ThemeName.DARK.value == "dark"

    def test_theme_creation(self) -> None:
        """Test creating themes from strings."""
        # Arrange - No setup needed for enum creation

        # Act - Create enum instances from strings

        # Assert - Verify enum instances match expected values
        assert ThemeName("iris-bloom") == ThemeName.IRIS_BLOOM
        assert ThemeName("light") == ThemeName.LIGHT
        assert ThemeName("dark") == ThemeName.DARK

    def test_invalid_theme(self) -> None:
        """Test that invalid theme names raise ValueError."""
        # Arrange - No setup needed for invalid input

        # Act & Assert - Verify that invalid theme name raises ValueError
        with pytest.raises(ValueError):
            ThemeName("invalid-theme")


@pytest.mark.unit
class TestThemeManager:
    """Test ThemeManager class."""

    def test_default_theme(self) -> None:
        """Test that default theme is IRIS_BLOOM."""
        # Arrange - Create theme manager instance

        # Act - Create manager (default theme is set in constructor)
        manager = ThemeManager()

        # Assert - Verify default theme is IRIS_BLOOM
        assert manager.current_theme == ThemeName.IRIS_BLOOM

    def test_theme_switching(self) -> None:
        """Test switching between themes."""
        # Arrange - Create theme manager instance
        manager = ThemeManager()

        # Act - Switch to light theme
        manager.switch_theme(ThemeName.LIGHT)

        # Assert - Verify theme was switched to light
        assert manager.current_theme.value == ThemeName.LIGHT.value

        # Act - Switch to dark theme
        manager.switch_theme(ThemeName.DARK)

        # Assert - Verify theme was switched to dark
        assert manager.current_theme.value == ThemeName.DARK.value

    def test_invalid_theme_switch(self) -> None:
        """Test that switching to invalid theme raises ValueError."""
        # Arrange - Create theme manager instance
        manager = ThemeManager()

        # Act & Assert - Verify that invalid theme switch raises ValueError
        with pytest.raises(ValueError, match="Unknown theme"):
            manager.switch_theme("invalid-theme")  # type: ignore[arg-type]

    def test_available_themes(self) -> None:
        """Test getting available themes."""
        # Arrange - Create theme manager instance
        manager = ThemeManager()

        # Act - Get available themes
        themes = manager.get_available_themes()

        # Assert - Verify all expected themes are available
        assert len(themes) == 3
        assert ThemeName.IRIS_BLOOM in themes
        assert ThemeName.LIGHT in themes
        assert ThemeName.DARK in themes

    def test_rich_theme_property(self) -> None:
        """Test that rich_theme property returns a theme."""
        # Arrange - Create theme manager instance
        manager = ThemeManager()

        # Act - Get rich theme
        theme = manager.rich_theme

        # Assert - Verify theme has expected structure
        assert theme is not None
        # Check that it has some expected keys
        assert "text" in theme.styles
        assert "command" in theme.styles

    def test_pt_style_property(self) -> None:
        """Test that pt_style property returns a style."""
        # Arrange - Create theme manager instance
        manager = ThemeManager()

        # Act - Get pt style
        style = manager.pt_style

        # Assert - Verify style is not None
        assert style is not None


@pytest.mark.unit
class TestGlobalThemeManager:
    """Test global theme manager functions."""

    def test_get_theme_manager(self) -> None:
        """Test getting the global theme manager."""
        # Arrange - No setup needed for global manager access

        # Act - Get global theme manager
        manager = get_theme_manager()

        # Assert - Verify manager is correct type and has default theme
        assert isinstance(manager, ThemeManager)
        # Reset to default theme to ensure consistent test state
        manager.switch_theme(ThemeName.IRIS_BLOOM)
        assert manager.current_theme == ThemeName.IRIS_BLOOM

    def test_switch_theme(self) -> None:
        """Test switching the global theme."""
        # Arrange - Get global manager and reset to default
        manager = get_theme_manager()
        manager.switch_theme(ThemeName.IRIS_BLOOM)

        # Act - Switch theme to light
        switch_theme(ThemeName.LIGHT)

        # Assert - Verify theme was switched to light
        assert manager.current_theme.value == ThemeName.LIGHT.value

        # Act - Switch theme back to iris bloom
        switch_theme(ThemeName.IRIS_BLOOM)

        # Assert - Verify theme was switched back to iris bloom
        assert manager.current_theme.value == ThemeName.IRIS_BLOOM.value
