"""Configuration management for Lily Petal."""

from lily.petal_config.defaults import create_default_config
from lily.petal_config.paths import (
    get_config_paths,
    get_project_config_dir,
    get_system_config_dir,
    get_user_config_dir,
)

__all__ = [
    "get_config_paths",
    "get_user_config_dir",
    "get_system_config_dir",
    "get_project_config_dir",
    "create_default_config",
]
