"""Tests for configuration management."""

import os
import tempfile
import tomllib
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import tomli_w

from lily.config import ConfigManager, LilyConfig
from lily.theme import ThemeName


@pytest.mark.unit
class TestLilyConfig:
    """Test LilyConfig model."""

    def test_default_config(self) -> None:
        """Test creating config with defaults."""
        # Arrange - No setup needed for default config creation

        # Act - Create config with minimal required parameters
        config = LilyConfig(openai_api_key="test-key")

        # Assert - Verify default values are set correctly
        assert config.openai_api_key == "test-key"
        assert config.model == "gpt-4"
        assert config.max_tokens == 4000
        assert config.temperature == 0.7
        assert config.theme == ThemeName.IRIS_BLOOM

    def test_custom_config(self) -> None:
        """Test creating config with custom values."""
        # Arrange - Define custom configuration parameters

        # Act - Create config with custom values
        config = LilyConfig(
            openai_api_key="custom-key",
            model="gpt-3.5-turbo",
            max_tokens=2000,
            temperature=0.5,
            theme=ThemeName.LIGHT,
        )

        # Assert - Verify custom values are set correctly
        assert config.openai_api_key == "custom-key"
        assert config.model == "gpt-3.5-turbo"
        assert config.max_tokens == 2000
        assert config.temperature == 0.5
        assert config.theme == ThemeName.LIGHT

    def test_api_key_validation(self) -> None:
        """Test API key validation."""
        # Arrange - No setup needed for validation tests

        # Act & Assert - Test valid API keys
        config = LilyConfig(openai_api_key="sk-test123456789")
        assert config.openai_api_key == "sk-test123456789"

        config = LilyConfig(openai_api_key="test-key")
        assert config.openai_api_key == "test-key"

        # Act & Assert - Test invalid API keys
        with pytest.raises(
            ValueError, match="OpenAI API key must be provided and valid"
        ):
            LilyConfig(openai_api_key="short")

        with pytest.raises(ValueError, match="OpenAI API key must be provided"):
            LilyConfig(openai_api_key="")

    def test_temperature_validation(self) -> None:
        """Test temperature validation."""
        # Arrange - No setup needed for validation tests

        # Act & Assert - Test valid temperatures
        LilyConfig(openai_api_key="test-key", temperature=0.0)
        LilyConfig(openai_api_key="test-key", temperature=1.0)
        LilyConfig(openai_api_key="test-key", temperature=2.0)

        # Act & Assert - Test invalid temperatures
        with pytest.raises(ValueError, match="Temperature must be between 0.0 and 2.0"):
            LilyConfig(openai_api_key="test-key", temperature=-0.1)

        with pytest.raises(ValueError, match="Temperature must be between 0.0 and 2.0"):
            LilyConfig(openai_api_key="test-key", temperature=2.1)

    def test_max_tokens_validation(self) -> None:
        """Test max tokens validation."""
        # Arrange - No setup needed for validation tests

        # Act & Assert - Test valid token counts
        LilyConfig(openai_api_key="test-key", max_tokens=1)
        LilyConfig(openai_api_key="test-key", max_tokens=1000)
        LilyConfig(openai_api_key="test-key", max_tokens=32000)

        # Act & Assert - Test invalid token counts
        with pytest.raises(ValueError, match="Max tokens must be between 1 and 32000"):
            LilyConfig(openai_api_key="test-key", max_tokens=0)

        with pytest.raises(ValueError, match="Max tokens must be between 1 and 32000"):
            LilyConfig(openai_api_key="test-key", max_tokens=32001)


@pytest.mark.unit
class TestConfigManager:
    """Test ConfigManager class."""

    def test_default_config_creation(self) -> None:
        """Test creating default configuration."""
        # Arrange - Create temporary directory and config path
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            # Act - Create default config with mocked environment variable
            with patch.dict(os.environ, {"OPENAI_API_KEY": "env-test-key"}):
                config = manager.create_default_config()

            # Assert - Verify default config has expected values
            assert config.openai_api_key == "env-test-key"
            assert config.model == "gpt-4"
            assert config.theme == ThemeName.IRIS_BLOOM

    def test_config_loading(self) -> None:
        """Test loading configuration from file."""
        # Arrange - Create temporary directory and test config file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"

            test_config = {
                "openai_api_key": "test-key",
                "model": "gpt-3.5-turbo",
                "max_tokens": 2000,
                "temperature": 0.5,
                "theme": "light",
            }

            with open(config_path, "wb") as f:
                tomli_w.dump(test_config, f)

            manager = ConfigManager(config_path)

            # Act - Load config from file
            config = manager.load_config()

            # Assert - Verify loaded config matches expected values
            assert config.openai_api_key == "test-key"
            assert config.model == "gpt-3.5-turbo"
            assert config.max_tokens == 2000
            assert config.temperature == 0.5
            assert config.theme == ThemeName.LIGHT

    def test_config_saving(self) -> None:
        """Test saving configuration to file."""
        # Arrange - Create temporary directory and config manager
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            config = LilyConfig(
                openai_api_key="save-test-key",
                model="gpt-4",
                theme=ThemeName.DARK,
            )

            # Act - Save config to file
            manager.save_config(config)

            # Assert - Verify file was created and contains correct data
            assert config_path.exists()

            # Act - Load config from file
            loaded_config = manager.load_config()

            # Assert - Verify loaded config matches saved config
            assert loaded_config.openai_api_key == "save-test-key"
            assert loaded_config.theme == ThemeName.DARK

    def test_config_validation(self) -> None:
        """Test configuration validation."""
        # Arrange - Create temporary directory and config manager
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            # Act & Assert - Test valid config validation
            config = LilyConfig(openai_api_key="test-valid-key")
            assert manager.validate_config(config) is True

            # Act & Assert - Test invalid config validation
            with pytest.raises(ValueError):
                invalid_config = LilyConfig(openai_api_key="")

    def test_config_update(self) -> None:
        """Test updating configuration."""
        # Arrange - Create temporary directory and initial config
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            initial_config = LilyConfig(openai_api_key="initial-key")
            manager.save_config(initial_config)

            # Act - Update config with new values
            updated_config = manager.update_config(
                model="gpt-3.5-turbo", theme=ThemeName.LIGHT
            )

            # Assert - Verify updated config has new values but preserves others
            assert updated_config.model == "gpt-3.5-turbo"
            assert updated_config.theme == ThemeName.LIGHT
            assert updated_config.openai_api_key == "initial-key"  # Unchanged

            # Act - Load config from file
            loaded_config = manager.load_config()

            # Assert - Verify file was updated with new values
            assert loaded_config.model == "gpt-3.5-turbo"
            assert loaded_config.theme == ThemeName.LIGHT

    def test_load_config_with_corrupted_file(self) -> None:
        """Test loading config when file exists but is corrupted."""
        # Arrange - Create temporary directory with corrupted config file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"

            # Write invalid TOML content
            with open(config_path, "w") as f:
                f.write("invalid toml content [")

            manager = ConfigManager(config_path)

            # Act - Load config (should fall back to default)
            with patch.dict(os.environ, {"OPENAI_API_KEY": "fallback-key"}):
                config = manager.load_config()

            # Assert - Should create default config due to corruption
            assert config.openai_api_key == "fallback-key"
            assert config.model == "gpt-4"
            assert config.theme == ThemeName.IRIS_BLOOM

    def test_save_config_with_directory_creation_error(self) -> None:
        """Test saving config when directory creation fails."""
        # Arrange - Create config manager with path in non-writable location
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file where we expect a directory
            bad_path = Path(temp_dir) / "bad" / "config.toml"
            bad_path.parent.mkdir()
            bad_path.parent.rmdir()  # Remove directory
            # Create a file instead of a directory to cause the error
            bad_path.parent.touch()

            manager = ConfigManager(bad_path)
            config = LilyConfig(openai_api_key="test-key")

            # Act & Assert - Should raise exception when directory creation fails
            with pytest.raises(Exception):
                manager.save_config(config)

    def test_create_default_config_without_env_var(self) -> None:
        """Test creating default config when environment variable is not set."""
        # Arrange - Create temporary directory and config manager
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            # Act - Create default config without environment variable
            with patch.dict(os.environ, {}, clear=True):
                # This will fail due to validation, but we can test the environment variable handling
                with pytest.raises(ValueError, match="OpenAI API key must be provided"):
                    manager.create_default_config()

            # Assert - Test completed successfully by raising the expected exception

    def test_validate_config_with_missing_api_key(self) -> None:
        """Test validation when API key is missing."""
        # Arrange - Create config manager and config without API key
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            # Create config with a valid API key first, then modify it
            config = LilyConfig(openai_api_key="test-key")
            # Use object.__setattr__ to bypass dataclass validation
            object.__setattr__(config, "openai_api_key", "")

            # Act - Validate config
            result = manager.validate_config(config)

            # Assert - Should return False for missing API key
            assert result is False

    def test_show_config(self) -> None:
        """Test displaying configuration."""
        # Arrange - Create config manager and config
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            config = LilyConfig(
                openai_api_key="test-key",
                model="gpt-3.5-turbo",
                max_tokens=2000,
                temperature=0.8,
                theme=ThemeName.DARK,
            )

            # Act - Show config (should not raise exception)
            manager.show_config(config)

            # Assert - Method should complete without error
            # The actual output is handled by rich console, so we just verify it doesn't crash

    def test_update_config_with_invalid_attributes(self) -> None:
        """Test updating config with attributes that don't exist."""
        # Arrange - Create temporary directory and initial config
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"
            manager = ConfigManager(config_path)

            initial_config = LilyConfig(openai_api_key="initial-key")
            manager.save_config(initial_config)

            # Act - Update config with invalid attribute
            updated_config = manager.update_config(
                invalid_attribute="should_be_ignored"
            )

            # Assert - Should ignore invalid attributes and preserve original config
            assert updated_config.openai_api_key == "initial-key"
            assert updated_config.model == "gpt-4"  # Default value

    def test_config_manager_with_custom_path(self) -> None:
        """Test ConfigManager initialization with custom path."""
        # Arrange - Create custom config path
        custom_path = Path("/tmp/custom_config.toml")

        # Act - Create manager with custom path
        manager = ConfigManager(custom_path)

        # Assert - Should use custom path
        assert manager.config_path == custom_path.expanduser()

    def test_config_manager_with_none_path(self) -> None:
        """Test ConfigManager initialization with None path (default)."""
        # Arrange - Mock home directory
        with patch.object(Path, "home", return_value=Path("/mock/home")):
            # Act - Create manager with None path
            manager = ConfigManager(None)

            # Assert - Should use default path
            expected_path = Path("/mock/home/.lily/config.toml")
            assert manager.config_path == expected_path

    def test_load_config_with_theme_enum_in_file(self) -> None:
        """Test loading config when theme is already an enum in the file."""
        # Arrange - Create temporary directory and test config file
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.toml"

            test_config = {
                "openai_api_key": "test-key",
                "theme": "dark",  # Use string instead of enum for TOML
            }

            with open(config_path, "wb") as f:
                tomli_w.dump(test_config, f)

            manager = ConfigManager(config_path)

            # Act - Load config from file
            config = manager.load_config()

            # Assert - Should handle string theme correctly
            assert config.theme == ThemeName.DARK

    def test_save_config_with_file_write_error(self) -> None:
        """Test saving config when file write fails."""
        # Arrange - Create config manager with path in non-writable location
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a read-only directory
            bad_dir = Path(temp_dir) / "readonly"
            bad_dir.mkdir()
            bad_dir.chmod(0o444)  # Read-only

            bad_path = bad_dir / "config.toml"
            manager = ConfigManager(bad_path)
            config = LilyConfig(openai_api_key="test-key")

            # Act & Assert - Should raise exception when file write fails
            with pytest.raises(Exception):
                manager.save_config(config)
