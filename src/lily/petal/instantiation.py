"""Petal object instantiation system."""

from typing import Any

from lily.petal.models import (
    IODecl,
    Param,
    Petal,
    StepBase,
)


class PetalInstantiator:
    """Instantiates Petal objects from configuration dictionaries."""

    def instantiate_petal(self, config: dict[str, Any]) -> Petal:
        """Instantiate a Petal object from configuration."""
        return Petal(**config)

    def instantiate_step(self, config: dict[str, Any]) -> StepBase:
        """Instantiate a StepBase object from configuration."""
        return StepBase(**config)

    def instantiate_param(self, config: dict[str, Any]) -> Param:
        """Instantiate a Param object from configuration."""
        return Param(**config)

    def instantiate_io_decl(self, config: dict[str, Any]) -> IODecl:
        """Instantiate an IODecl object from configuration."""
        return IODecl(**config)
