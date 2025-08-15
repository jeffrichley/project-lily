"""Petal DSL parser with simple YAML parsing.

This parser provides basic YAML parsing for Petal workflow files without
complex configuration management dependencies.
"""

from pathlib import Path
from typing import TypedDict

import yaml

from lily.petal.config import (
    _convert_outputs,
    _convert_params,
    _convert_steps,
    load_petal,
)
from lily.petal.expressions import ExpressionEvaluator
from lily.petal.models import Petal, StepBase
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
        """Parse a Petal file using the consolidated YAML parsing.

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
            # Use the consolidated load_petal function
            petal = load_petal(file_path)

            # Validate the workflow
            self._validate_petal(petal)

            return petal

        except Exception as e:
            if isinstance(e, PetalParseError):
                raise
            raise PetalParseError(f"Failed to parse Petal file: {e}") from e

    def parse_string(self, content: str) -> Petal:
        """Parse Petal content from a string."""
        try:
            # Parse YAML content directly
            data = yaml.safe_load(content)

            # Validate basic structure
            if not isinstance(data, dict):
                raise PetalParseError("Petal content must contain a YAML object")

            if "petal" not in data:
                raise PetalParseError("Missing required 'petal' field")

            if data["petal"] != "1":
                raise PetalParseError(f"Unsupported Petal version: {data['petal']}")

            # Convert directly to Petal with strategic type ignores
            petal = Petal(
                petal=str(data["petal"]),  # type: ignore
                name=str(data["name"]),
                description=(
                    str(data.get("description")) if data.get("description") else None
                ),
                extends=data.get("extends"),
                composition_enabled=data.get("composition_enabled", True),
                params=_convert_params(data.get("params", {})),
                env=dict(data.get("env", {})),
                vars=dict(data.get("vars", {})),
                steps=_convert_steps(data.get("steps", [])),
                outputs=_convert_outputs(data.get("outputs", [])),
                on_error=_convert_steps(data.get("on_error", [])),
                artifacts=data.get("artifacts"),
            )

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
            self._validate_step_env_templates(step)
            self._validate_step_input_templates(step)
            self._validate_step_output_templates(step)

    def _validate_step_env_templates(self, step: StepBase) -> None:
        """Validate environment variable templates in a step."""
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

    def _validate_step_input_templates(self, step: StepBase) -> None:
        """Validate input templates in a step."""
        if step.inputs:
            for input_name, input_decl in step.inputs.items():
                if (
                    hasattr(input_decl, "from_")
                    and input_decl.from_
                    and isinstance(input_decl.from_, str)
                    and "{{" in input_decl.from_
                ):
                    is_valid, error = self.template_engine.validate_petal_template(
                        input_decl.from_
                    )
                    if not is_valid:
                        raise PetalParseError(
                            f"Invalid template in step {step.id}.inputs.{input_name}.from: {error}"
                        )

    def _validate_step_output_templates(self, step: StepBase) -> None:
        """Validate output templates in a step."""
        if step.outputs:
            for output_name, output_decl in step.outputs.items():
                if (
                    hasattr(output_decl, "from_")
                    and output_decl.from_
                    and isinstance(output_decl.from_, str)
                    and "{{" in output_decl.from_
                ):
                    is_valid, error = self.template_engine.validate_petal_template(
                        output_decl.from_
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
        vars_set = self._extract_vars_section_variables(petal.vars)
        steps_dict = self._extract_steps_variables(petal.steps)

        return TemplateVariables(vars=vars_set, steps=steps_dict)

    def _extract_vars_section_variables(self, vars_data: dict[str, str]) -> set[str]:
        """Extract template variables from the vars section."""
        vars_set = set()
        for var_value in vars_data.values():
            if isinstance(var_value, str):
                vars_set.update(self.template_engine.get_required_variables(var_value))
        return vars_set

    def _extract_steps_variables(self, steps: list[StepBase]) -> dict[str, set[str]]:
        """Extract template variables from all steps."""
        steps_dict = {}
        for step in steps:
            step_vars = self._extract_step_variables(step)
            if step_vars:
                steps_dict[step.id] = step_vars
        return steps_dict

    def _extract_step_variables(self, step: StepBase) -> set[str]:
        """Extract template variables from a single step."""
        step_vars = set()
        step_vars.update(self._extract_env_variables(step))
        step_vars.update(self._extract_input_variables(step))
        step_vars.update(self._extract_output_variables(step))
        return step_vars

    def _extract_env_variables(self, step: StepBase) -> set[str]:
        """Extract template variables from environment variables."""
        env_vars = set()
        if step.env:
            for env_value in step.env.values():
                if isinstance(env_value, str):
                    env_vars.update(
                        self.template_engine.get_required_variables(env_value)
                    )
        return env_vars

    def _extract_input_variables(self, step: StepBase) -> set[str]:
        """Extract template variables from input declarations."""
        input_vars = set()
        if step.inputs:
            for input_decl in step.inputs.values():
                if (
                    hasattr(input_decl, "from_")
                    and input_decl.from_
                    and isinstance(input_decl.from_, str)
                ):
                    input_vars.update(
                        self.template_engine.get_required_variables(input_decl.from_)
                    )
        return input_vars

    def _extract_output_variables(self, step: StepBase) -> set[str]:
        """Extract template variables from output declarations."""
        output_vars = set()
        if step.outputs:
            for output_decl in step.outputs.values():
                if (
                    hasattr(output_decl, "from_")
                    and output_decl.from_
                    and isinstance(output_decl.from_, str)
                ):
                    output_vars.update(
                        self.template_engine.get_required_variables(output_decl.from_)
                    )
        return output_vars
