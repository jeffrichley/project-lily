"""Configuration schemas for Petal DSL objects.

This module provides configuration schemas for Petal objects.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParamConfig:
    """Configuration schema for Param objects."""

    type: str  # Will be validated at runtime
    required: bool = False
    default: Any = None  # Will be validated at runtime
    help: str | None = None


@dataclass
class IODeclConfig:
    """Configuration schema for IODecl objects."""

    type: str | None = None  # Will be validated at runtime
    required: bool = False
    json_schema: dict[str, Any] | None = None
    from_: str | None = None  # template/expr
    path: str | None = None  # when materialized


@dataclass
class StepBaseConfig:
    """Configuration schema for StepBase objects."""

    id: str
    uses: str  # Will be validated at runtime
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None  # Will be validated at runtime
    with_: dict[str, Any] | None = None


# Step Type Configurations
@dataclass
class ShellStepConfig:
    """Configuration schema for shell step type."""

    id: str
    uses: str = "shell"
    command: str = ""
    shell: str = "bash"  # bash, zsh, fish, sh
    working_directory: str | None = None
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class PythonStepConfig:
    """Configuration schema for python step type."""

    id: str
    uses: str = "python"
    script: str = ""
    python_version: str = "3.12"
    virtual_env: str | None = None
    requirements_file: str | None = None
    allow_network: bool = False  # Security default
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class LLMStepConfig:
    """Configuration schema for llm step type."""

    id: str
    uses: str = "llm"
    model: str = "gpt-4"
    prompt: str = ""
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 1000
    provider: str = "openai"  # openai, anthropic, local
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class HumanStepConfig:
    """Configuration schema for human step type."""

    id: str
    uses: str = "human"
    message: str = ""
    prompt: str = ""
    timeout: str = "1h"  # Default human step timeout
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class ForeachStepConfig:
    """Configuration schema for foreach step type."""

    id: str
    uses: str = "foreach"
    items: list[Any] = field(default_factory=list)
    item_var: str = "item"
    index_var: str = "index"
    steps: list[dict[str, Any]] = field(default_factory=list)
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class IncludeStepConfig:
    """Configuration schema for include step type."""

    id: str
    uses: str = "include"
    file: str = ""
    params: dict[str, Any] = field(default_factory=dict)
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class ToolStepConfig:
    """Configuration schema for tool step type."""

    id: str
    uses: str = "tool"
    tool_name: str = ""
    tool_version: str = "latest"
    args: dict[str, Any] = field(default_factory=dict)
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    cache: dict[str, Any] | None = None
    resources: dict[str, Any] | None = None
    adapter: str | None = None
    with_: dict[str, Any] | None = None


@dataclass
class PetalConfig:
    """Configuration schema for Petal objects."""

    petal: str  # Will be validated at runtime
    name: str
    description: str | None = None
    extends: str | None = None
    composition_enabled: bool = True
    params: dict[str, Any] = field(default_factory=dict)
    env: dict[str, str] = field(default_factory=dict)
    vars: dict[str, str] = field(default_factory=dict)
    steps: list[dict[str, Any]] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)
    on_error: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] | None = None


@dataclass
class LockFileConfig:
    """Configuration schema for LockFile objects."""

    schema_version: str  # Will be validated at runtime
    petal_version: str
    provenance: dict[str, Any]
    spec_hash: str
    execution_contract: dict[str, Any]
    env_policy: dict[str, Any]
    artifacts: dict[str, Any]
    registry_pins: dict[str, Any]
    params: dict[str, Any]
    plan: dict[str, Any]


def get_config_schemas() -> dict[str, type]:
    """Get all available configuration schemas.

    Returns:
        Dictionary mapping schema names to schema classes
    """
    return {
        "param": ParamConfig,
        "io_decl": IODeclConfig,
        "step_base": StepBaseConfig,
        "petal": PetalConfig,
        "lock_file": LockFileConfig,
        "shell_step": ShellStepConfig,
        "python_step": PythonStepConfig,
        "llm_step": LLMStepConfig,
        "human_step": HumanStepConfig,
        "foreach_step": ForeachStepConfig,
        "include_step": IncludeStepConfig,
        "tool_step": ToolStepConfig,
    }
