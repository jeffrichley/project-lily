"""Type-safe configuration for Petal DSL.

This module provides a Google-style approach to YAML configuration parsing that balances
type safety with practical constraints from external libraries.

TYPE SAFETY STRATEGY:
====================

1. **External Library Boundary**: YAML parsing libraries (PyYAML) return 'Any'
   types, which we cannot control. This is the fundamental constraint.

2. **Strategic Type Ignores**: We use type ignores ONLY at the boundary between external
   YAML parsing and our strict model validation, not throughout our codebase.

3. **Runtime Validation**: Our models (Param, IODecl, StepBase, Petal) validate all inputs
   at runtime, providing safety despite type system limitations.

4. **Type-Safe Configuration**: The PetalConfig class uses proper types throughout,
   maintaining type safety in our own code.

WHY TYPE IGNORES ARE NECESSARY:
===============================

The type ignores in this file exist because:

- YAML parsing returns flexible types (str, int, dict, etc.)
- Our models expect strict Literal types for validation
- The type system cannot track the runtime validation that makes this safe
- We validate all inputs at runtime in our model constructors

Example type mismatch:
- YAML: {"type": "str", "required": true}
- Model expects: Literal["str", "int", "float", ...] for type field
- Runtime validation ensures only valid values are accepted

This approach follows Google's pattern of strategic type ignores at external boundaries
while maintaining strict type safety throughout the rest of the codebase.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from lily.petal.models import IODecl, Param, Petal, StepBase


@dataclass
class PetalConfig:
    """Type-safe Petal configuration."""

    petal: str
    name: str
    description: str | None = None
    extends: str | None = None  # NEW: Support for inheritance
    composition_enabled: bool = True  # NEW: Explicit composition flag
    params: dict[str, dict[str, Any]] = field(default_factory=dict)
    env: dict[str, str] = field(default_factory=dict)
    vars: dict[str, str] = field(default_factory=dict)
    steps: list[dict[str, Any]] = field(default_factory=list)
    outputs: list[dict[str, Any]] = field(default_factory=list)
    on_error: list[dict[str, Any]] = field(default_factory=list)
    artifacts: dict[str, Any] | None = None


def load_petal_config(file_path: Path) -> PetalConfig:
    """Load Petal configuration using YAML with type safety.

    This provides compile-time and runtime type safety.
    """
    # Load YAML file
    with open(file_path) as f:
        config_data = yaml.safe_load(f)

    # Validate basic structure
    if not isinstance(config_data, dict):
        raise ValueError("Petal file must contain a YAML object")

    if "petal" not in config_data:
        raise ValueError("Missing required 'petal' field")

    if config_data["petal"] != "1":
        raise ValueError(f"Unsupported Petal version: {config_data['petal']}")

    # Convert to our typed config with proper type casting
    return PetalConfig(
        petal=str(config_data["petal"]),
        name=str(config_data["name"]),
        description=(
            str(config_data.get("description"))
            if config_data.get("description")
            else None
        ),
        params=dict(config_data.get("params", {})),
        env=dict(config_data.get("env", {})),
        vars=dict(config_data.get("vars", {})),
        steps=list(config_data.get("steps", [])),
        outputs=list(config_data.get("outputs", [])),
        on_error=list(config_data.get("on_error", [])),
        artifacts=config_data.get("artifacts"),
    )


def convert_config_to_petal(config: PetalConfig) -> Petal:
    """Convert PetalConfig to Petal model with proper type conversion.

    This function handles the conversion from the configuration format to the
    runtime model format, ensuring type safety throughout the process.
    """
    # Convert parameters to Param objects
    params = {}
    for param_name, param_data in config.params.items():
        if isinstance(param_data, dict):
            params[param_name] = Param(**param_data)
        else:
            # Handle simple string type case
            params[param_name] = Param(type=str(param_data))

    # Convert steps to StepBase objects
    steps = []
    for step_data in config.steps:
        if not isinstance(step_data, dict):
            raise ValueError(f"Step must be a dictionary, got {type(step_data)}")

        if "id" not in step_data:
            raise ValueError("Step missing required 'id' field")
        if "uses" not in step_data:
            raise ValueError(
                f"Step {step_data.get('id', 'unknown')} missing required 'uses' field"
            )

        # Convert inputs/outputs to IODecl objects
        inputs = {}
        for input_name, input_data in step_data.get("inputs", {}).items():
            if isinstance(input_data, dict):
                inputs[input_name] = IODecl(**input_data)
            else:
                inputs[input_name] = IODecl(
                    type=str(input_data) if input_data else None
                )

        outputs = {}
        for output_name, output_data in step_data.get("outputs", {}).items():
            if isinstance(output_data, dict):
                outputs[output_name] = IODecl(**output_data)
            else:
                outputs[output_name] = IODecl(
                    type=str(output_data) if output_data else None
                )

        step = StepBase(
            id=str(step_data["id"]),
            uses=str(step_data["uses"]),
            needs=step_data.get("needs", []),
            if_=step_data.get("if_"),
            timeout=step_data.get("timeout"),
            retries=step_data.get("retries"),
            env=step_data.get("env"),
            inputs=inputs,
            outputs=outputs,
            cache=step_data.get("cache"),
            resources=step_data.get("resources"),
            adapter=step_data.get("adapter"),
            with_=step_data.get("with_"),
        )
        steps.append(step)

    # Create Petal object
    return Petal(
        petal=config.petal,
        name=config.name,
        description=config.description,
        extends=config.extends,
        composition_enabled=config.composition_enabled,
        params=params,
        env=config.env,
        vars=config.vars,
        steps=steps,
        outputs=config.outputs,
        on_error=config.on_error,
        artifacts=config.artifacts,
    )
