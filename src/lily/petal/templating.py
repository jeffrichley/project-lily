"""Template engine for Petal DSL with security constraints."""

import hashlib
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, StrictUndefined, TemplateError

from lily.types import TemplateValue

if TYPE_CHECKING:
    pass


class PetalTemplateError(Exception):
    """Exception raised for Petal template errors."""

    pass


class ConstrainedJinjaEnvironment:
    """Jinja2 environment with security constraints for Petal DSL."""

    def __init__(self) -> None:
        """Initialize the constrained Jinja environment."""
        self.env = Environment(
            undefined=StrictUndefined,
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register only whitelisted filters
        self._register_allowed_filters()

        # Disable potentially dangerous features
        self.env.globals = {}
        self.env.tests = {}

    def _register_allowed_filters(self) -> None:
        """Register only the allowed filters."""
        # Custom filters for Petal DSL
        self.env.filters["now"] = self._filter_now
        self.env.filters["hash"] = self._filter_hash
        self.env.filters["tojson"] = self._filter_tojson
        self.env.filters["abspath"] = self._filter_abspath
        self.env.filters["relpath"] = self._filter_relpath
        self.env.filters["env"] = self._filter_env
        self.env.filters["basename"] = self._filter_basename
        self.env.filters["dirname"] = self._filter_dirname
        self.env.filters["uuid"] = self._filter_uuid
        self.env.filters["joinpath"] = self._filter_joinpath

    def _filter_now(
        self, value: str | None = None, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Get current timestamp in specified format."""
        # If value is provided, use it as the format string
        if value is not None:
            format_str = value
        return datetime.now().strftime(format_str)

    def _filter_hash(self, value: str, algorithm: str = "sha256") -> str:
        """Generate hash of a string value."""
        if algorithm not in ["md5", "sha1", "sha256", "sha512"]:
            raise PetalTemplateError(f"Unsupported hash algorithm: {algorithm}")

        hash_obj = hashlib.new(algorithm)
        hash_obj.update(value.encode("utf-8"))
        return hash_obj.hexdigest()

    def _filter_tojson(self, value: TemplateValue) -> str:
        """Convert value to JSON string."""
        return json.dumps(value, ensure_ascii=False)

    def _filter_abspath(self, path: str) -> str:
        """Convert relative path to absolute path."""
        return str(Path(path).resolve())

    def _filter_relpath(self, path: str, start: str = ".") -> str:
        """Convert absolute path to relative path."""
        return str(Path(path).relative_to(Path(start)))

    def _filter_env(self, key: str, default: str = "") -> str:
        """Get environment variable value."""
        return os.environ.get(key, default)

    def _filter_basename(self, path: str) -> str:
        """Get basename of a path."""
        return Path(path).name

    def _filter_dirname(self, path: str) -> str:
        """Get directory name of a path."""
        return str(Path(path).parent)

    def _filter_uuid(self) -> str:
        """Generate a UUID string."""
        return str(uuid.uuid4())

    def _filter_joinpath(self, *paths: str) -> str:
        """Join path components."""
        return str(Path(*paths))

    def render(self, template_str: str, context: dict[str, TemplateValue]) -> str:
        """Render a template string with the given context."""
        try:
            template = self.env.from_string(template_str)
            return template.render(**context)
        except TemplateError as e:
            raise PetalTemplateError(f"Template rendering error: {e}") from e
        except Exception as e:
            raise PetalTemplateError(
                f"Unexpected error during template rendering: {e}"
            ) from e

    def validate_template(self, template_str: str) -> bool:
        """Validate that a template string is syntactically correct."""
        try:
            self.env.from_string(template_str)
            return True
        except TemplateError:
            return False

    def get_template_variables(self, template_str: str) -> set[str]:
        """Extract variable names from a template string."""
        try:
            # Use regex to find all variable names in {{ variable }} patterns
            pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}"
            matches = re.findall(pattern, template_str)
            return set(matches)
        except Exception:
            return set()


class PetalTemplateEngine:
    """Main template engine for Petal DSL."""

    def __init__(self) -> None:
        """Initialize the Petal template engine."""
        self.env = ConstrainedJinjaEnvironment()

    def render_single_pass(
        self, template_str: str, context: dict[str, TemplateValue]
    ) -> str:
        """Render template in a single pass (no nested rendering)."""
        # Check for potential nested template patterns
        if self._has_nested_templates(template_str):
            raise PetalTemplateError("Nested template rendering is not allowed")

        return self.env.render(template_str, context)

    def _has_nested_templates(self, template_str: str) -> bool:
        """Check if template contains potential nested template patterns."""
        # Look for patterns that might indicate nested rendering
        # Only flag actual nested templates, not multiple separate templates
        nested_patterns = [
            r"\{\{.*\{\{.*\}\}.*\}\}",  # Nested {{ {{ }} }}
            r"\{\{.*render.*\}\}",  # render function calls
            r"\{\{.*include.*\}\}",  # include statements
            r"\{\{.*extends.*\}\}",  # extends statements
        ]

        for pattern in nested_patterns:
            if re.search(pattern, template_str, re.IGNORECASE):
                return True

        return False

    def validate_petal_template(self, template_str: str) -> tuple[bool, str | None]:
        """Validate a Petal template and return (is_valid, error_message)."""
        if not self.env.validate_template(template_str):
            return False, "Invalid template syntax"

        if self._has_nested_templates(template_str):
            return False, "Nested template rendering is not allowed"

        return True, None

    def preview_template(
        self, template_str: str, context: dict[str, TemplateValue]
    ) -> str:
        """Generate a preview of template rendering without executing."""
        try:
            return self.render_single_pass(template_str, context)
        except PetalTemplateError as e:
            return f"[TEMPLATE ERROR: {e}]"

    def get_required_variables(self, template_str: str) -> set[str]:
        """Get the set of variables required by a template."""
        return self.env.get_template_variables(template_str)
