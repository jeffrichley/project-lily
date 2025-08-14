"""Petal DSL parser with simple YAML parsing.

This parser provides basic YAML parsing for Petal workflow files without
complex configuration management dependencies.
"""

from pathlib import Path
from typing import TypedDict

import yaml

from lily.petal.expressions import ExpressionEvaluator
from lily.petal.models import Petal
from lily.petal.templating import PetalTemplateEngine


class TemplateVariables(TypedDict):
    """Template variables structure returned by get_template_variables."""

    vars: set[str]
    steps: dict[str, set[str]]


class PetalParseError(Exception):
    """Custom exception for Petal parsing errors."""

    pass


class PetalParser:
    """Parser for Petal DSL workflow files with simple YAML parsing."""

    def __init__(self) -> None:
        """Initialize the Petal parser."""
        self.template_engine = PetalTemplateEngine()
        self.expression_evaluator = ExpressionEvaluator()

    def parse_file(self, file_path: str | Path) -> Petal:
        """Parse a Petal file using simple YAML parsing.

        Args:
            file_path: Path to the Petal file

        Returns:
            Parsed Petal object
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise PetalParseError(f"File not found: {file_path}")

        if file_path.suffix not in [".petal", ".yaml", ".yml"]:
            raise PetalParseError(f"Unsupported file extension: {file_path.suffix}")

        try:
            # Load the file with YAML
            with open(file_path) as f:
                data = yaml.safe_load(f)

            # Convert to Petal model
            petal = self._dict_to_petal(data)

            # Validate the workflow
            self._validate_petal(petal)

            return petal

        except Exception as e:
            if isinstance(e, PetalParseError):
                raise
            raise PetalParseError(f"Failed to parse Petal file: {e}") from e

    def _dict_to_petal(self, data: dict) -> Petal:
        """Convert dictionary to Petal model."""
        if not isinstance(data, dict):
            raise PetalParseError(f"Expected dictionary, got {type(data)}")

        # Check if the data has the required fields
        if "petal" not in data:
            raise PetalParseError("Missing key 'petal'")
        if "name" not in data:
            raise PetalParseError("Missing key 'name'")

        # Convert parameters to Param objects
        params = {}
        for param_name, param_data in data.get("params", {}).items():
            if isinstance(param_data, dict):
                from lily.petal.models import Param

                params[param_name] = Param(**param_data)
            else:
                # Handle simple string type case
                from lily.petal.models import Param

                params[param_name] = Param(type=str(param_data))

        # Convert steps to StepBase objects
        steps = []
        for step_data in data.get("steps", []):
            if not isinstance(step_data, dict):
                raise PetalParseError(
                    f"Step must be a dictionary, got {type(step_data)}"
                )

            if "id" not in step_data:
                raise PetalParseError("Step missing required 'id' field")
            if "uses" not in step_data:
                raise PetalParseError(
                    f"Step {step_data.get('id', 'unknown')} missing required 'uses' field"
                )

            # Convert step data to StepBase
            from lily.petal.models import IODecl, StepBase

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
                if_=step_data.get("if"),
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

        # Convert to Petal model
        return Petal(
            petal=str(data["petal"]),
            name=str(data["name"]),
            description=(
                str(data.get("description")) if data.get("description") else None
            ),
            extends=str(data.get("extends")) if data.get("extends") else None,
            composition_enabled=bool(data.get("composition_enabled", True)),
            params=params,
            env=data.get("env", {}),
            vars=data.get("vars", {}),
            steps=steps,
            outputs=data.get("outputs", []),
            on_error=data.get("on_error", []),
            artifacts=data.get("artifacts", {}) if data.get("artifacts") else None,
        )

    def parse_string(self, content: str) -> Petal:
        """Parse Petal content from a string."""
        try:
            # Parse YAML content directly
            data = yaml.safe_load(content)

            # Convert to Petal model
            petal = self._dict_to_petal(data)

            # Validate the workflow
            self._validate_petal(petal)

            return petal

        except Exception as e:
            if isinstance(e, PetalParseError):
                raise
            raise PetalParseError(f"Failed to parse Petal content: {e}") from e

    def validate_file(self, file_path: str | Path) -> tuple[bool, str | None]:
        """Validate a Petal file without parsing it completely.

        Args:
            file_path: Path to the Petal file

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            self.parse_file(file_path)
            return True, None
        except PetalParseError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def _validate_petal(self, petal: Petal) -> None:
        """Validate a Petal object."""
        # Validate templates and expressions
        self._validate_petal_templates(petal)
        self._validate_petal_expressions(petal)

        # Validate step types
        self._validate_step_types(petal)

    def _validate_petal_templates(self, petal: Petal) -> None:
        """Validate all templates in a Petal object."""
        self._validate_vars_templates(petal)
        self._validate_step_templates(petal)

    def _validate_vars_templates(self, petal: Petal) -> None:
        """Validate templates in vars section."""
        for var_name, var_value in petal.vars.items():
            if isinstance(var_value, str) and "{{" in var_value:
                is_valid, error = self.template_engine.validate_petal_template(
                    var_value
                )
                if not is_valid:
                    raise PetalParseError(
                        f"Invalid template in vars.{var_name}: {error}"
                    )

    def _validate_step_templates(self, petal: Petal) -> None:
        """Validate templates in steps section."""
        for step in petal.steps:
            # Validate step environment templates
            if step.env:
                for env_name, env_value in step.env.items():
                    if isinstance(env_value, str) and "{{" in env_value:
                        is_valid, error = self.template_engine.validate_petal_template(
                            env_value
                        )
                        if not is_valid:
                            raise PetalParseError(
                                f"Invalid template in step {step.id}.env.{env_name}: {error}"
                            )

            # Validate step input templates
            if step.inputs:
                for input_name, input_decl in step.inputs.items():
                    if hasattr(input_decl, "from_") and input_decl.from_:
                        if (
                            isinstance(input_decl.from_, str)
                            and "{{" in input_decl.from_
                        ):
                            is_valid, error = (
                                self.template_engine.validate_petal_template(
                                    input_decl.from_
                                )
                            )
                            if not is_valid:
                                raise PetalParseError(
                                    f"Invalid template in step {step.id}.inputs.{input_name}.from: {error}"
                                )

            # Validate step output templates
            if step.outputs:
                for output_name, output_decl in step.outputs.items():
                    if hasattr(output_decl, "from_") and output_decl.from_:
                        if (
                            isinstance(output_decl.from_, str)
                            and "{{" in output_decl.from_
                        ):
                            is_valid, error = (
                                self.template_engine.validate_petal_template(
                                    output_decl.from_
                                )
                            )
                            if not is_valid:
                                raise PetalParseError(
                                    f"Invalid template in step {step.id}.outputs.{output_name}.from: {error}"
                                )

    def _validate_petal_expressions(self, petal: Petal) -> None:
        """Validate all expressions in a Petal object."""
        for step in petal.steps:
            if step.if_:
                is_valid, error = self.expression_evaluator.validate(step.if_)
                if not is_valid:
                    raise PetalParseError(
                        f"Invalid expression in step {step.id}.if: {error}"
                    )

    def _validate_step_types(self, petal: Petal) -> None:
        """Validate that all step types are supported."""
        for step in petal.steps:
            if step.uses not in [
                "shell",
                "python",
                "llm",
                "human",
                "foreach",
                "include",
                "tool",
            ]:
                raise PetalParseError(
                    f"Unsupported step type '{step.uses}' in step {step.id}"
                )

    def get_template_variables(self, petal: Petal) -> TemplateVariables:
        """Extract template variables from a Petal object."""
        vars_set = set()
        steps_dict = {}

        # Extract variables from vars section
        for var_value in petal.vars.values():
            if isinstance(var_value, str):
                vars_set.update(self.template_engine.extract_variables(var_value))

        # Extract variables from steps
        for step in petal.steps:
            step_vars = set()

            # Environment variables
            if step.env:
                for env_value in step.env.values():
                    if isinstance(env_value, str):
                        step_vars.update(
                            self.template_engine.extract_variables(env_value)
                        )

            # Input variables
            if step.inputs:
                for input_decl in step.inputs.values():
                    if hasattr(input_decl, "from_") and input_decl.from_:
                        if isinstance(input_decl.from_, str):
                            step_vars.update(
                                self.template_engine.extract_variables(input_decl.from_)
                            )

            # Output variables
            if step.outputs:
                for output_decl in step.outputs.values():
                    if hasattr(output_decl, "from_") and output_decl.from_:
                        if isinstance(output_decl.from_, str):
                            step_vars.update(
                                self.template_engine.extract_variables(
                                    output_decl.from_
                                )
                            )

            if step_vars:
                steps_dict[step.id] = step_vars

        return TemplateVariables(vars=vars_set, steps=steps_dict)
