"""Core type protocols for Petal executor."""

from typing import Protocol, runtime_checkable


@runtime_checkable
class StateValue(Protocol):
    """Protocol for valid workflow state values.

    Supports: str, int, float, bool, list[StateValue], dict[str, StateValue]
    """

    # No methods needed - just structural typing
    pass


@runtime_checkable
class StepResult(Protocol):
    """Protocol for step execution results.

    Tools return dict[str, StateValue] which implements this protocol.
    """

    # No methods needed - just structural typing
    pass


@runtime_checkable
class StepConfig(Protocol):
    """Protocol for step configuration."""

    id: str
    uses: str
    writes: list[str]
    # Other fields will be added as needed


@runtime_checkable
class ContextProvider(Protocol):
    """Protocol for context resolution."""

    def get_context(self) -> dict[str, StateValue]:
        """Get execution context."""
        ...


# Type aliases for convenience
StateDict = dict[str, StateValue]
StepResultDict = dict[str, StateValue]
