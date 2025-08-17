"""Unit tests for CLI entry point functionality."""

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from lily.cli import app, show_banner


@pytest.mark.unit
class TestCLIEntryPoint:
    """Test CLI entry point functionality."""

    def test_cli_app_creation(self) -> None:
        """Test that CLI app is properly configured."""
        # Arrange - No setup needed

        # Act - Access app configuration

        # Assert - Verify app has correct configuration
        assert app.info.name == "lily"
        assert app.info.help is not None and "Lily" in app.info.help
        # Note: rich_markup_mode is not available in this version of Typer

    def test_show_banner(self) -> None:
        """Test banner display functionality."""
        # Arrange - Mock console to capture output
        with patch("lily.cli.utils.get_console") as mock_get_console:
            mock_console = Mock()
            mock_get_console.return_value = mock_console

            # Act - Show banner
            show_banner()

            # Assert - Verify banner was displayed
            mock_console.print.assert_called_once()
            # Check that a Panel was created (banner is a Panel)
            call_args = mock_console.print.call_args[0][0]
            assert hasattr(call_args, "renderable")

    def test_version_command(self) -> None:
        """Test version command functionality."""
        # Arrange - Create CLI runner
        runner = CliRunner()

        # Act - Run version command
        result = runner.invoke(app, ["version"])

        # Assert - Verify version command works
        assert result.exit_code == 0
        assert "version" in result.stdout.lower() or "lily" in result.stdout.lower()
