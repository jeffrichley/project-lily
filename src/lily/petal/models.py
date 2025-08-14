"""Dataclass models for the Lily Petal DSL schema."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from lily.types import (
    ArtifactsDict,
    CacheDict,
    JsonValue,
    LockFileDict,
    ResourceDict,
    RetryDict,
    StepIODict,
    WithDict,
)


def validate_param_default(param_type: str, default_value: object) -> None:
    """Validate that default value matches the declared type."""
    if default_value is None:
        return

    type_validators: dict[str, tuple[type | tuple[type, ...], str]] = {
        "str": (str, "string"),
        "int": (int, "integer"),
        "float": ((int, float), "number"),
        "bool": (bool, "boolean"),
        "path": ((str, Path), "string or Path"),
        "file": ((str, Path), "string or Path"),
        "dir": ((str, Path), "string or Path"),
        "json": ((dict, list), "dict or list"),
        "secret": (str, "string"),
        "bytes": (bytes, "bytes"),
    }

    if param_type in type_validators:
        expected_type, type_name = type_validators[param_type]
        if not isinstance(default_value, expected_type):
            raise ValueError(
                f"Default value must be {type_name} for type '{param_type}', got {type(default_value)}"
            )


def validate_retries(retries: RetryDict | None) -> None:
    """Validate retry configuration."""
    if retries is None:
        return

    if not isinstance(retries, dict):
        raise ValueError("Retries must be a dictionary")

    required_keys = {"max"}
    if not required_keys.issubset(retries.keys()):
        raise ValueError(f"Retries must contain required keys: {required_keys}")

    if not isinstance(retries["max"], int) or retries["max"] < 0:
        raise ValueError("Retry max must be a non-negative integer")

    if "backoff" in retries and not re.match(r"^\d+[smhd]$", str(retries["backoff"])):
        raise ValueError(
            "Backoff must be in format: <number><unit> where unit is s, m, h, or d"
        )


def validate_step_id(step_id: str) -> None:
    """Validate step ID format."""
    if not re.match(r"^[a-zA-Z0-9_-]+$", step_id):
        raise ValueError("Step ID must match pattern: ^[a-zA-Z0-9_-]+$")


def validate_timeout(timeout: str | None) -> None:
    """Validate timeout format."""
    if timeout is not None and not re.match(r"^\d+[smhd]$", timeout):
        raise ValueError(
            "Timeout must be in format: <number><unit> where unit is s, m, h, or d"
        )


def validate_spec_hash(spec_hash: str) -> None:
    """Validate spec hash format."""
    if not re.match(r"^sha256:[a-fA-F0-9]{64}$", spec_hash):
        raise ValueError("Spec hash must be in format: sha256:<64 hex chars>")


def validate_petal_name(name: str) -> str:
    """Validate and normalize workflow name."""
    normalized = name.strip()
    if not normalized:
        raise ValueError("Petal name cannot be empty")
    return normalized


def validate_unique_step_ids(steps: list["StepBase"]) -> None:
    """Validate that steps have unique IDs."""
    step_ids = [step.id for step in steps]
    if len(step_ids) != len(set(step_ids)):
        raise ValueError("All step IDs must be unique")


@dataclass
class Param:
    """Parameter definition for Petal workflows."""

    type: Literal[
        "str", "int", "float", "bool", "path", "file", "dir", "json", "secret", "bytes"
    ]
    required: bool = False
    default: str | int | float | bool | Path | JsonValue | bytes | None = None
    help: str | None = None

    def __post_init__(self) -> None:
        """Validate the parameter after initialization."""
        # Validate type is a valid literal value
        valid_types = [
            "str",
            "int",
            "float",
            "bool",
            "path",
            "file",
            "dir",
            "json",
            "secret",
            "bytes",
        ]
        if self.type not in valid_types:
            raise ValueError(
                f"Invalid type '{self.type}'. Must be one of: {valid_types}"
            )

        validate_param_default(self.type, self.default)


@dataclass
class IODecl:
    """Input/Output declaration for step parameters."""

    type: (
        Literal[
            "str",
            "int",
            "float",
            "bool",
            "path",
            "file",
            "dir",
            "json",
            "secret",
            "bytes",
        ]
        | None
    ) = None
    required: bool = False
    json_schema: dict[str, JsonValue] | None = None  # for json
    from_: str | None = None  # template/expr
    path: str | None = None  # when materialized

    def __post_init__(self) -> None:
        """Validate the I/O declaration after initialization."""
        # Validate type if provided
        if self.type is not None:
            valid_types = [
                "str",
                "int",
                "float",
                "bool",
                "path",
                "file",
                "dir",
                "json",
                "secret",
                "bytes",
            ]
            if self.type not in valid_types:
                raise ValueError(
                    f"Invalid type '{self.type}'. Must be one of: {valid_types}"
                )

        # Validate json_schema is a dict if provided
        if self.json_schema is not None and not isinstance(self.json_schema, dict):
            raise ValueError("json_schema must be a dictionary")


@dataclass
class StepBase:
    """Base step definition for Petal workflows."""

    id: str
    uses: Literal["shell", "python", "llm", "human", "foreach", "include", "tool"]
    needs: list[str] = field(default_factory=list)
    if_: str | None = None
    timeout: str | None = None
    retries: RetryDict | None = None
    env: dict[str, str] | None = None
    inputs: dict[str, IODecl] = field(default_factory=dict)
    outputs: dict[str, IODecl] = field(default_factory=dict)
    cache: CacheDict | None = None
    resources: ResourceDict | None = None
    adapter: Literal["process", "docker", "python", "http"] | None = None
    with_: WithDict | None = None

    def __post_init__(self) -> None:
        """Validate the step after initialization."""
        # Validate uses is a valid literal value
        valid_uses = ["shell", "python", "llm", "human", "foreach", "include", "tool"]
        if self.uses not in valid_uses:
            raise ValueError(
                f"Invalid uses '{self.uses}'. Must be one of: {valid_uses}"
            )

        # Validate adapter if provided
        if self.adapter is not None:
            valid_adapters = ["process", "docker", "python", "http"]
            if self.adapter not in valid_adapters:
                raise ValueError(
                    f"Invalid adapter '{self.adapter}'. Must be one of: {valid_adapters}"
                )

        validate_step_id(self.id)
        validate_timeout(self.timeout)
        validate_retries(self.retries)


@dataclass
class Petal:
    """Main Petal workflow definition."""

    petal: Literal["1"]
    name: str
    description: str | None = None
    extends: str | None = None  # NEW: Support for inheritance
    composition_enabled: bool = True  # NEW: Explicit composition flag
    params: dict[str, Param] = field(default_factory=dict)
    env: dict[str, str] = field(default_factory=dict)
    vars: dict[str, str] = field(default_factory=dict)
    steps: list[StepBase] = field(default_factory=list)
    outputs: list[StepIODict] = field(default_factory=list)
    on_error: list[StepBase] = field(default_factory=list)
    artifacts: ArtifactsDict | None = None

    def __post_init__(self) -> None:
        """Validate the petal after initialization."""
        # Validate petal version
        if self.petal != "1":
            raise ValueError(f"Invalid petal version '{self.petal}'. Must be '1'")

        self.name = validate_petal_name(self.name)
        validate_unique_step_ids(self.steps)


@dataclass
class LockFile:
    """Lock file containing frozen, executable workflow plan."""

    schema_version: Literal["1"]
    petal_version: str
    provenance: LockFileDict  # sources, composer metadata
    spec_hash: str  # content-addressed hash of resolved AST
    execution_contract: LockFileDict  # render_passes, expression_lang, defaults_frozen
    env_policy: LockFileDict  # network_default, secrets_sources, allowed_binaries
    artifacts: LockFileDict  # backend, root
    registry_pins: LockFileDict  # tools, models with digests
    params: LockFileDict  # fully resolved key-value pairs
    plan: LockFileDict  # resolved DAG of steps

    def __post_init__(self) -> None:
        """Validate the lock file after initialization."""
        # Validate schema version
        if self.schema_version != "1":
            raise ValueError(
                f"Invalid schema version '{self.schema_version}'. Must be '1'"
            )

        validate_spec_hash(self.spec_hash)
