"""Petal DSL parser for loading and validating workflow files."""

import tempfile
from pathlib import Path
from typing import TypedDict

from lily.petal.config import convert_config_to_petal, load_petal_config
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
    """Parser for Petal DSL workflow files."""

    def __init__(self) -> None:
        """Initialize the Petal parser."""
        self.template_engine = PetalTemplateEngine()
        self.expression_evaluator = ExpressionEvaluator()

    def _parse_yaml_content(self, content: str) -> Petal:
        """Parse YAML content and return validated Petal object."""
        # Write content to temporary file for Hydra
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            # Use Hydra for type-safe loading
            config = load_petal_config(temp_path)
            return convert_config_to_petal(config)
        finally:
            # Clean up temporary file
            temp_path.unlink(missing_ok=True)

    def parse_file(self, file_path: str | Path) -> Petal:
        """Parse a Petal file and return a Petal object."""
        file_path = Path(file_path)

        if not file_path.exists():
            raise PetalParseError(f"File not found: {file_path}")

        if file_path.suffix not in [".petal", ".yaml", ".yml"]:
            raise PetalParseError(f"Unsupported file extension: {file_path.suffix}")

        try:
            # Use Hydra for type-safe loading
            config = load_petal_config(file_path)
            petal = convert_config_to_petal(config)

            # Validate templates and expressions
            self._validate_petal_templates(petal)
            self._validate_petal_expressions(petal)

            return petal

        except Exception as e:
            if isinstance(e, PetalParseError):
                raise
            raise PetalParseError(f"Failed to parse Petal file: {e}") from e

    def parse_string(self, content: str) -> Petal:
        """Parse Petal content from a string."""
        try:
            # Parse and validate YAML content using Hydra
            petal = self._parse_yaml_content(content)

            # Validate templates and expressions
            self._validate_petal_templates(petal)
            self._validate_petal_expressions(petal)

            return petal

        except Exception as e:
            if isinstance(e, PetalParseError):
                raise
            raise PetalParseError(f"Failed to parse Petal content: {e}") from e

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
        """Validate templates in step sections."""
        for step in petal.steps:
            self._validate_step_env_templates(step)
            self._validate_step_io_templates(step)

    def _validate_step_env_templates(self, step: StepBase) -> None:
        """Validate environment variable templates in a step."""
        if not step.env:
            return

        for env_key, env_value in step.env.items():
            if isinstance(env_value, str) and "{{" in env_value:
                is_valid, error = self.template_engine.validate_petal_template(
                    env_value
                )
                if not is_valid:
                    raise PetalParseError(
                        f"Invalid template in step {step.id}.env.{env_key}: {error}"
                    )

    def _validate_step_io_templates(self, step: StepBase) -> None:
        """Validate input/output templates in a step."""
        # Validate input templates
        for input_name, input_decl in step.inputs.items():
            if input_decl.from_ and "{{" in input_decl.from_:
                is_valid, error = self.template_engine.validate_petal_template(
                    input_decl.from_
                )
                if not is_valid:
                    raise PetalParseError(
                        f"Invalid template in step {step.id}.inputs.{input_name}.from: {error}"
                    )

        # Validate output templates
        for output_name, output_decl in step.outputs.items():
            if output_decl.path and "{{" in output_decl.path:
                is_valid, error = self.template_engine.validate_petal_template(
                    output_decl.path
                )
                if not is_valid:
                    raise PetalParseError(
                        f"Invalid template in step {step.id}.outputs.{output_name}.path: {error}"
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

    def validate_file(self, file_path: str | Path) -> tuple[bool, str | None]:
        """Validate a Petal file without parsing it completely."""
        try:
            self.parse_file(file_path)
            return True, None
        except PetalParseError as e:
            return False, str(e)

    def get_template_variables(self, petal: Petal) -> TemplateVariables:
        """Extract all template variables from a Petal object."""
        variables: TemplateVariables = {
            "vars": self._extract_vars_template_variables(petal),
            "steps": self._extract_steps_template_variables(petal),
        }
        return variables

    def _extract_vars_template_variables(self, petal: Petal) -> set[str]:
        """Extract template variables from vars section."""
        vars_variables = set()
        for var_value in petal.vars.values():
            if isinstance(var_value, str) and "{{" in var_value:
                vars_variables.update(
                    self.template_engine.get_required_variables(var_value)
                )
        return vars_variables

    def _extract_steps_template_variables(self, petal: Petal) -> dict[str, set[str]]:
        """Extract template variables from steps section."""
        steps_variables = {}
        for step in petal.steps:
            step_vars = self._extract_step_template_variables(step)
            if step_vars:
                steps_variables[step.id] = step_vars
        return steps_variables

    def _extract_step_template_variables(self, step: StepBase) -> set[str]:
        """Extract template variables from a single step."""
        step_vars = set()

        # Extract from env variables
        step_vars.update(self._extract_template_vars_from_dict(step.env))

        # Extract from inputs
        for input_decl in step.inputs.values():
            if input_decl.from_ and "{{" in input_decl.from_:
                step_vars.update(
                    self.template_engine.get_required_variables(input_decl.from_)
                )

        # Extract from outputs
        for output_decl in step.outputs.values():
            if output_decl.path and "{{" in output_decl.path:
                step_vars.update(
                    self.template_engine.get_required_variables(output_decl.path)
                )

        return step_vars

    def _extract_template_vars_from_dict(self, data: dict[str, str] | None) -> set[str]:
        """Extract template variables from a dictionary of strings."""
        if not data:
            return set()

        vars_set = set()
        for value in data.values():
            if isinstance(value, str) and "{{" in value:
                vars_set.update(self.template_engine.get_required_variables(value))
        return vars_set

    def get_expression_identifiers(self, petal: Petal) -> dict[str, set[str]]:
        """Extract all expression identifiers from a Petal object."""
        identifiers = {}

        for step in petal.steps:
            if step.if_:
                identifiers[step.id] = self.expression_evaluator.get_identifiers(
                    step.if_
                )

        return identifiers
