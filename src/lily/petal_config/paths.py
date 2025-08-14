"""Configuration path management utilities."""

from pathlib import Path


def get_user_config_dir() -> Path:
    """Get user configuration directory."""
    return Path.home() / ".lily" / "config"


def get_system_config_dir() -> Path:
    """Get system configuration directory."""
    return Path("/etc/lily/config")


def get_project_config_dir() -> Path:
    """Get project configuration directory."""
    return Path.cwd() / "conf"


def get_config_paths() -> list[Path]:
    """Get configuration paths in priority order (highest to lowest priority)."""
    paths = []

    # 1. Project configs (highest priority)
    project_config = get_project_config_dir()
    if project_config.exists():
        paths.append(project_config)

    # 2. User configs (medium priority)
    user_config = get_user_config_dir()
    if user_config.exists():
        paths.append(user_config)

    # 3. System configs (lowest priority)
    system_config = get_system_config_dir()
    if system_config.exists():
        paths.append(system_config)

    return paths


def ensure_config_dir(path: Path) -> Path:
    """Ensure a configuration directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_config_file_path(config_dir: Path, config_name: str = "config") -> Path:
    """Get the full path to a configuration file."""
    return config_dir / f"{config_name}.yaml"
