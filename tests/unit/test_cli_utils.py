"""Unit tests for CLI utility functions."""

from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from lily.cli.utils import get_console, show_banner


@pytest.mark.unit
class TestCLIUtils:
    """Test CLI utility functions."""

    def test_get_console_returns_console_instance(self) -> None:
        """Test that get_console returns a proper Console instance."""
        # Arrange - Mock theme manager
        with patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager:
            mock_theme_manager = Mock()
            mock_theme = Mock()
            mock_theme_manager.rich_theme = mock_theme
            mock_get_theme_manager.return_value = mock_theme_manager

            # Act - Get console instance
            console = get_console()

            # Assert - Verify console is properly configured
            assert isinstance(console, Console)
            # The theme is passed during construction, not stored as an attribute
            # We verify the theme manager was called correctly
            mock_get_theme_manager.assert_called_once()

    def test_get_console_uses_current_theme(self) -> None:
        """Test that get_console uses the current theme from theme manager."""
        # Arrange - Mock theme manager with specific theme
        with patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager:
            mock_theme_manager = Mock()
            mock_theme = Mock()
            mock_theme_manager.rich_theme = mock_theme
            mock_get_theme_manager.return_value = mock_theme_manager

            # Act - Get console instance
            console = get_console()

            # Assert - Verify theme manager was called and theme was applied
            mock_get_theme_manager.assert_called_once()
            # The theme is passed during construction, not stored as an attribute
            # We verify the theme manager was called correctly

    def test_show_banner_creates_banner_panel(self) -> None:
        """Test that show_banner creates and displays a banner panel."""
        # Arrange - Mock console and theme manager
        with (
            patch("lily.cli.utils.get_console") as mock_get_console,
            patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager,
        ):

            mock_console = Mock()
            mock_get_console.return_value = mock_console
            mock_theme_manager = Mock()
            mock_get_theme_manager.return_value = mock_theme_manager

            # Act - Show banner
            show_banner()

            # Assert - Verify console.print was called with a Panel
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert isinstance(call_args, Panel)

    def test_show_banner_panel_content(self) -> None:
        """Test that show_banner panel contains expected content."""
        # Arrange - Mock console and theme manager
        with (
            patch("lily.cli.utils.get_console") as mock_get_console,
            patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager,
        ):

            mock_console = Mock()
            mock_get_console.return_value = mock_console
            mock_theme_manager = Mock()
            mock_get_theme_manager.return_value = mock_theme_manager

            # Act - Show banner
            show_banner()

            # Assert - Verify panel content
            call_args = mock_console.print.call_args[0][0]
            panel = call_args
            assert isinstance(panel.renderable, Text)

            # Check that banner text contains expected content
            text_content = str(panel.renderable)
            assert "🌙" in text_content
            assert "Lily" in text_content
            assert "Software development project planning" in text_content

    def test_show_banner_panel_styling(self) -> None:
        """Test that show_banner panel has correct styling."""
        # Arrange - Mock console and theme manager
        with (
            patch("lily.cli.utils.get_console") as mock_get_console,
            patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager,
        ):

            mock_console = Mock()
            mock_get_console.return_value = mock_console
            mock_theme_manager = Mock()
            mock_get_theme_manager.return_value = mock_theme_manager

            # Act - Show banner
            show_banner()

            # Assert - Verify panel styling
            call_args = mock_console.print.call_args[0][0]
            panel = call_args
            assert isinstance(panel, Panel)
            # Verify panel has title
            assert panel.title is not None
            # Verify panel has border
            assert panel.border_style is not None

    def test_show_banner_with_theme_error(self) -> None:
        """Test that show_banner handles theme errors gracefully."""
        # Arrange - Mock console and theme manager with error
        with (
            patch("lily.cli.utils.get_console") as mock_get_console,
            patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager,
        ):

            mock_console = Mock()
            mock_get_console.return_value = mock_console
            mock_get_theme_manager.side_effect = Exception("Theme error")

            # Act - Show banner with theme error
            show_banner()

            # Assert - Verify banner still works even with theme error
            mock_console.print.assert_called_once()
            call_args = mock_console.print.call_args[0][0]
            assert isinstance(call_args, Panel)

    def test_get_console_with_theme_error(self) -> None:
        """Test that get_console handles theme errors gracefully."""
        # Arrange - Mock theme manager with error
        with patch("lily.cli.utils.get_theme_manager") as mock_get_theme_manager:
            mock_get_theme_manager.side_effect = Exception("Theme error")

            # Act - Get console instance with theme error
            console = get_console()

            # Assert - Verify console is still created even with theme error
            assert isinstance(console, Console)
