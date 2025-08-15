"""Custom step implementations for Petal workflows.

This module provides example custom step classes that can be instantiated
in Petal configurations.
"""

from dataclasses import dataclass
from pathlib import Path

from lily.petal.models import StepBase


@dataclass
class CustomShellStep(StepBase):
    """Custom shell step with additional features."""

    shell_type: str = "bash"  # bash, zsh, fish, etc.
    working_directory: str | None = None
    timeout_seconds: int = 300

    def __post_init__(self) -> None:
        """Validate custom shell step configuration."""
        # Skip parent validation for custom steps to avoid uses field conflicts
        # super().__post_init__()

        if self.shell_type not in ["bash", "zsh", "fish", "sh"]:
            raise ValueError(f"Unsupported shell type: {self.shell_type}")

        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")


@dataclass
class PythonScriptStep(StepBase):
    """Custom Python script step."""

    script_path: str | None = None
    python_version: str = "3.12"
    virtual_env: str | None = None
    requirements_file: str | None = None

    def __post_init__(self) -> None:
        """Validate Python script step configuration."""
        # Skip parent validation for custom steps to avoid uses field conflicts
        # super().__post_init__()

        if self.script_path and not Path(self.script_path).exists():
            raise ValueError(f"Script file not found: {self.script_path}")

        # Validate Python version format
        if not self.python_version.startswith(("3.", "2.")):
            raise ValueError(f"Invalid Python version: {self.python_version}")


@dataclass
class DockerStep(StepBase):
    """Custom Docker step."""

    image: str = "python:3.12"  # Default image
    dockerfile: str | None = None
    build_context: str | None = None
    ports: dict[str, str] | None = None
    volumes: dict[str, str] | None = None
    environment: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Validate Docker step configuration."""
        # Skip parent validation for custom steps to avoid uses field conflicts
        # super().__post_init__()

        if not self.image:
            raise ValueError("Docker image is required")

        # Validate port mapping format
        if self.ports:
            for host_port, container_port in self.ports.items():
                try:
                    int(host_port)
                    int(container_port)
                except ValueError as err:
                    raise ValueError(
                        f"Invalid port mapping: {host_port}:{container_port}"
                    ) from err


@dataclass
class HTTPRequestStep(StepBase):
    """Custom HTTP request step."""

    url: str = "http://localhost"  # Default URL
    method: str = "GET"
    headers: dict[str, str] | None = None
    body: str | None = None
    timeout: str = "30s"
    retry_count: int = 3

    def __post_init__(self) -> None:
        """Validate HTTP request step configuration."""
        # Skip parent validation for custom steps to avoid uses field conflicts
        # super().__post_init__()

        if not self.url:
            raise ValueError("URL is required")

        if self.method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            raise ValueError(f"Unsupported HTTP method: {self.method}")

        if self.timeout and not self.timeout.endswith(("s", "m", "h", "d")):
            raise ValueError(
                "Timeout must be in format: <number><unit> where unit is s, m, h, or d"
            )

        if self.retry_count < 0:
            raise ValueError("Retry count must be non-negative")


@dataclass
class FileProcessingStep(StepBase):
    """Custom file processing step."""

    input_pattern: str = "*.txt"  # Default pattern
    output_directory: str | None = None
    file_type: str = "auto"  # auto, text, binary, json, csv, etc.
    encoding: str = "utf-8"
    chunk_size: int = 1024

    def __post_init__(self) -> None:
        """Validate file processing step configuration."""
        # Skip parent validation for custom steps to avoid uses field conflicts
        # super().__post_init__()

        if not self.input_pattern:
            raise ValueError("Input pattern is required")

        if self.chunk_size <= 0:
            raise ValueError("Chunk size must be positive")

        if self.file_type not in [
            "auto",
            "text",
            "binary",
            "json",
            "csv",
            "yaml",
            "xml",
        ]:
            raise ValueError(f"Unsupported file type: {self.file_type}")


@dataclass
class DatabaseStep(StepBase):
    """Custom database step."""

    connection_string: str = "sqlite:///test.db"  # Default connection
    query: str | None = None
    script_file: str | None = None
    database_type: str = "sqlite"  # sqlite, postgresql, mysql, etc.
    transaction_mode: str = "auto"  # auto, manual, none

    def __post_init__(self) -> None:
        """Validate database step configuration."""
        # Skip parent validation for custom steps to avoid uses field conflicts
        # super().__post_init__()

        if not self.connection_string:
            raise ValueError("Connection string is required")

        if not self.query and not self.script_file:
            raise ValueError("Either query or script_file must be provided")

        if self.database_type not in [
            "sqlite",
            "postgresql",
            "mysql",
            "oracle",
            "sqlserver",
        ]:
            raise ValueError(f"Unsupported database type: {self.database_type}")

        if self.transaction_mode not in ["auto", "manual", "none"]:
            raise ValueError(f"Unsupported transaction mode: {self.transaction_mode}")
