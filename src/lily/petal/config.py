"""Direct YAML to Petal conversion with strategic type safety.

This module provides direct YAML → Petal conversion with strategic type ignores
only at the external YAML parsing boundary.

TYPE SAFETY STRATEGY:
====================

1. **External Library Boundary**: YAML parsing libraries (PyYAML) return 'Any'
   types, which we cannot control. This is the fundamental constraint.

2. **Strategic Type Ignores**: We use type ignores ONLY at the boundary between external
   YAML parsing and our strict model validation, not throughout our codebase.

3. **Runtime Validation**: Our models (Param, IODecl, StepBase, Petal) validate all inputs
   at runtime, providing safety despite type system limitations.

4. **Direct Conversion**: YAML → Petal with no intermediate config objects.

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

from pathlib import Path
from typing import Any

import yaml

from lily.petal.models import IODecl, Param, Petal, StepBase


def load_petal(file_path: Path) -> Petal:
    """Load Petal directly from YAML with strategic type safety.

    This provides compile-time and runtime type safety with minimal complexity.
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

    # Convert directly to Petal with strategic type ignores
    return Petal(
        petal="1",  # We already validated this above
        name=str(config_data["name"]),
        description=(
            str(config_data.get("description"))
            if config_data.get("description")
            else None
        ),
        extends=config_data.get("extends"),
        composition_enabled=config_data.get("composition_enabled", True),
        params=_convert_params(config_data.get("params", {})),
        env=dict(config_data.get("env", {})),
        vars=dict(config_data.get("vars", {})),
        steps=_convert_steps(config_data.get("steps", [])),
        outputs=_convert_outputs(config_data.get("outputs", [])),
        on_error=_convert_steps(config_data.get("on_error", [])),
        artifacts=config_data.get("artifacts"),
    )


def _convert_params(params_config: dict[str, Any]) -> dict[str, Param]:
    """Convert parameters configuration to Param objects."""
    params = {}
    for param_name, param_data in params_config.items():
        if isinstance(param_data, dict):
            params[param_name] = Param(**param_data)
        else:
            # Handle simple string type case
            params[param_name] = Param(type="str")  # Default to str for simple values
    return params


def _convert_steps(steps_config: list[dict[str, Any]]) -> list[StepBase]:
    """Convert steps configuration to StepBase objects."""
    steps = []
    for step_data in steps_config:
        if not isinstance(step_data, dict):
            raise ValueError(f"Step must be a dictionary, got {type(step_data)}")

        if "id" not in step_data:
            raise ValueError("Step missing required 'id' field")
        if "uses" not in step_data:
            raise ValueError(
                f"Step {step_data.get('id', 'unknown')} missing required 'uses' field"
            )

        # Convert inputs/outputs to IODecl objects
        inputs = _convert_io_declarations(step_data.get("inputs", {}))
        outputs = _convert_io_declarations(step_data.get("outputs", {}))

        step = StepBase(
            id=str(step_data["id"]),
            uses=str(step_data["uses"]),  # type: ignore
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
    return steps


def _convert_outputs(outputs_config: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert outputs configuration (keeping as dict for now)."""
    return outputs_config


def _convert_io_declarations(io_config: dict[str, Any]) -> dict[str, IODecl]:
    """Convert input/output declarations to IODecl objects."""
    declarations = {}
    for name, data in io_config.items():
        if isinstance(data, dict):
            declarations[name] = IODecl(**data)
        else:
            declarations[name] = IODecl(type="str" if data else None)  # Default to str
    return declarations
