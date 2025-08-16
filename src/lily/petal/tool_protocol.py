"""Tool protocol for Petal workflow system."""

from typing import Protocol, runtime_checkable

from lily.petal.executor.tools import ToolContext
from lily.petal.executor.types import StepConfig, StepResultDict


@runtime_checkable
class Tool(Protocol):
    """Protocol for all Petal tools."""

    @property
    def name(self) -> str:
        """The name of the tool (e.g., 'debug.echo')."""
        ...

    @property
    def step_config_class(self) -> type[StepConfig]:
        """The Pydantic step config class for this tool's configuration."""
        ...

    def execute(self, ctx: ToolContext, step: StepConfig) -> StepResultDict:
        """Execute the tool with the given context and step configuration."""
        ...

    def validate(self, step: StepConfig) -> bool:
        """Validate that the step configuration is correct for this tool."""
        # Default implementation - can be overridden
        return step.uses == self.name

    def get_description(self) -> str:
        """Get a description of what this tool does."""
        # Default implementation - can be overridden
        return getattr(self, "__doc__", None) or f"Tool: {self.name}"
