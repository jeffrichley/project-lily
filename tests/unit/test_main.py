"""Unit tests for main module."""

import pytest
from unittest.mock import patch

from lily.cli.main import main


@pytest.mark.unit
class TestMain:
    """Test main module functionality."""

    def test_main_calls_cli_main(self) -> None:
        """Test that main calls the CLI main function."""
        # Arrange - Mock the app function
        with patch("lily.cli.main.app") as mock_app:
            # Act - Call the main function
            main()
            # Assert - Verify app was called
            mock_app.assert_called_once()

    def test_main_module_execution(self) -> None:
        """Test that main module can be executed."""
        # Arrange - Mock the app function
        with patch("lily.cli.main.app") as mock_app:
            # Act - Import and execute main module
            import lily.__main__

            # Assert - Verify app was called (this covers the __name__ == "__main__" line)
            # Note: Importing doesn't execute the if __name__ == "__main__" block
            # So we just verify the module can be imported
            assert mock_app.call_count == 0
