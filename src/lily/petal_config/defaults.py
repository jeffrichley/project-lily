"""Default configuration templates for Lily Petal."""

from pathlib import Path


def create_default_config(config_file: Path) -> None:
    """Create a default configuration file."""
    default_config = """# Lily Petal Configuration

defaults:
  - db: mysql
  - profiles: local
  - _self_

# Environment variables
env:
  LILY_LOG_LEVEL: "INFO"
  LILY_CACHE_ENABLED: "true"
  LILY_CACHE_DIR: ".lily/cache"
  LILY_ARTIFACTS_DIR: ".lily/artifacts"

# Parameters
params:
  debug: false
  dry_run: false
  parallel: true
  max_workers: 4
  timeout: "300s"

# Variables
vars:
  timestamp: "{{ now('%Y%m%d-%H%M%S') }}"
  run_id: "{{ uuid() }}"
"""
    config_file.write_text(default_config)


def create_default_db_config(config_dir: Path, db_type: str) -> None:
    """Create a default database configuration file."""
    db_configs = {
        "mysql": """db:
  type: "mysql"
  host: "localhost"
  port: 3306
  user: "lily_user"
  password: "{{ env.DB_PASSWORD }}"
  database: "lily_workflows"

env:
  DB_TYPE: "mysql"
  DB_HOST: "localhost"
  DB_PORT: "3306"
""",
        "postgresql": """db:
  type: "postgresql"
  host: "localhost"
  port: 5432
  user: "lily_user"
  password: "{{ env.DB_PASSWORD }}"
  database: "lily_workflows"

env:
  DB_TYPE: "postgresql"
  DB_HOST: "localhost"
  DB_PORT: "5432"
""",
        "sqlite": """db:
  type: "sqlite"
  path: "{{ project_root }}/data/workflows.db"

env:
  DB_TYPE: "sqlite"
  DB_PATH: "{{ project_root }}/data/workflows.db"
""",
    }

    if db_type not in db_configs:
        raise ValueError(f"Unknown database type: {db_type}")

    db_dir = config_dir / "db"
    db_dir.mkdir(exist_ok=True)

    db_file = db_dir / f"{db_type}.yaml"
    db_file.write_text(db_configs[db_type])


def create_default_profile_config(config_dir: Path, profile_name: str) -> None:
    """Create a default profile configuration file."""
    profile_configs = {
        "local": """profiles:
  name: "local"
  debug: true
  dry_run: false
  parallel: false

env:
  LILY_LOG_LEVEL: "DEBUG"
  LILY_CACHE_ENABLED: "true"

params:
  max_workers: 2
  timeout: "30s"
  retry_attempts: 0
""",
        "ci": """profiles:
  name: "ci"
  debug: false
  dry_run: false
  parallel: true

env:
  LILY_LOG_LEVEL: "INFO"
  LILY_CACHE_ENABLED: "false"

params:
  max_workers: 4
  timeout: "300s"
  retry_attempts: 3
""",
        "production": """profiles:
  name: "production"
  debug: false
  dry_run: false
  parallel: true

env:
  LILY_LOG_LEVEL: "WARNING"
  LILY_CACHE_ENABLED: "true"

params:
  max_workers: 16
  timeout: "1800s"
  retry_attempts: 3
""",
    }

    if profile_name not in profile_configs:
        raise ValueError(f"Unknown profile: {profile_name}")

    profiles_dir = config_dir / "profiles"
    profiles_dir.mkdir(exist_ok=True)

    profile_file = profiles_dir / f"{profile_name}.yaml"
    profile_file.write_text(profile_configs[profile_name])


def create_default_workflow_config(config_dir: Path, workflow_name: str) -> None:
    """Create a default workflow configuration file."""
    workflow_configs = {
        "video_processing": """workflows:
  type: "video_processing"

params:
  input_format: "mp4"
  output_format: "mp4"
  quality: "high"
  resolution: "1080p"

env:
  FFMPEG_PATH: "/usr/bin/ffmpeg"
  FFPROBE_PATH: "/usr/bin/ffprobe"

vars:
  output_dir: "output/{{ hash(params.input_file) }}"
  temp_dir: "{{ output_dir }}/temp"
""",
        "data_pipeline": """workflows:
  type: "data_pipeline"

params:
  batch_size: 1000
  parallel: true
  retry_failed: true

env:
  DATA_SOURCE: "{{ env.DATA_SOURCE }}"
  DATA_SINK: "{{ env.DATA_SINK }}"

vars:
  batch_dir: "{{ temp_dir }}/batches"
  results_dir: "{{ output_dir }}/results"
""",
    }

    if workflow_name not in workflow_configs:
        raise ValueError(f"Unknown workflow: {workflow_name}")

    workflows_dir = config_dir / "workflows"
    workflows_dir.mkdir(exist_ok=True)

    workflow_file = workflows_dir / f"{workflow_name}.yaml"
    workflow_file.write_text(workflow_configs[workflow_name])


def create_default_adapter_config(config_dir: Path, adapter_name: str) -> None:
    """Create a default adapter configuration file."""
    adapter_configs = {
        "process": """adapters:
  type: "process"

env:
  PROCESS_TIMEOUT: "300s"
  PROCESS_WORKING_DIR: "{{ project_root }}"

params:
  capture_output: true
  check_returncode: true
""",
        "docker": """adapters:
  type: "docker"

env:
  DOCKER_IMAGE: "lily/petal:latest"
  DOCKER_NETWORK: "lily-network"

params:
  privileged: false
  remove: true
  volumes:
    - "{{ project_root }}:/workspace"
""",
        "http": """adapters:
  type: "http"

env:
  HTTP_TIMEOUT: "30s"
  HTTP_RETRIES: 3

params:
  verify_ssl: true
  follow_redirects: true
""",
    }

    if adapter_name not in adapter_configs:
        raise ValueError(f"Unknown adapter: {adapter_name}")

    adapters_dir = config_dir / "adapters"
    adapters_dir.mkdir(exist_ok=True)

    adapter_file = adapters_dir / f"{adapter_name}.yaml"
    adapter_file.write_text(adapter_configs[adapter_name])
