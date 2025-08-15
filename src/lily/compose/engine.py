"""Main composition engine for Petal workflows."""

from pathlib import Path

from lily.petal.models import Petal
from lily.petal.parser import PetalParser
from lily.petal.validator import PetalValidator


class CompositionEngine:
    """Main composition engine for Petal workflows."""

    def __init__(self) -> None:
        """Initialize the composition engine."""
        self._parser: PetalParser | None = None  # Lazy loading
        self.parser: PetalParser | None = None  # Public parser attribute for tests

    def _get_parser(self) -> PetalParser:
        """Get parser instance with lazy loading."""
        if self._parser is None:
            self._parser = PetalParser()
            self.parser = self._parser  # Set public attribute
        assert self._parser is not None  # Help mypy understand this is never None
        return self._parser

    def compose_petal(self, petal_file: str | Path) -> Petal:
        """Compose a Petal workflow from a file.

        Args:
            petal_file: Path to the Petal workflow file

        Returns:
            Parsed Petal workflow
        """
        # Load the Petal file
        parser = self._get_parser()
        petal = parser.parse_file(petal_file)

        # Validate the workflow
        validator = PetalValidator()
        is_valid, errors = validator.validate(petal)

        if not is_valid:
            raise ValueError(f"Invalid Petal workflow: {errors}")

        return petal

    def get_composition_info(
        self, petal_file: str | Path
    ) -> dict[str, dict[str, object | bool | list[str]]]:
        """Get information about the Petal workflow without executing it.

        Args:
            petal_file: Path to the Petal workflow file

        Returns:
            Workflow information
        """
        # Load the Petal file
        parser = self._get_parser()
        petal = parser.parse_file(petal_file)

        # Create info structure
        info: dict[str, dict[str, object | bool | list[str]]] = {
            "petal": {
                "name": petal.name,
                "description": petal.description,
                "extends": petal.extends,
                "composition_enabled": petal.composition_enabled,
                "parameters": len(petal.params),
                "environment_variables": len(petal.env),
                "variables": len(petal.vars),
                "steps": len(petal.steps),
            },
            "composition": {"valid": True, "errors": []},
        }

        # Validate composition
        validator = PetalValidator()
        is_valid, errors = validator.validate(petal)
        info["composition"]["valid"] = is_valid
        info["composition"]["errors"] = errors

        return info
