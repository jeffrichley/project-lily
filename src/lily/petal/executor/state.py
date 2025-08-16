"""Workflow state management for Petal executor."""

from pathlib import Path

import structlog

from lily.petal.enums import StepStatus
from lily.petal.executor.types import StateDict, StateValue, StepConfig, StepResultDict


class WorkflowState:
    """Manages the state of a Petal workflow execution."""

    def __init__(
        self,
        run_id: str,
        run_dir: Path,
        params: StateDict,
        env: dict[str, str],
    ) -> None:
        """Initialize workflow state."""
        self.run_id = run_id
        self.run_dir = run_dir
        self.params = params
        self.env = env
        self.logger = structlog.get_logger()

        # Core engine state (what it actually needs)
        self.state: StateDict = {}
        self.step_status: dict[str, StepStatus] = {}
        self.step_results: dict[str, StepResultDict] = {}
        self.current_step: str | None = None

    def update(self, step_id: str, outputs: StepResultDict) -> None:
        """Update state with step outputs."""
        self.state.update(outputs)
        self.step_results[step_id] = outputs
        self.logger.info(
            "Updated workflow state",
            step_id=step_id,
            outputs=outputs,
            state_keys=list(self.state.keys()),
        )

    def set_step_status(self, step_id: str, status: StepStatus) -> None:
        """Set step status (engine needs this for coordination)."""
        self.step_status[step_id] = status
        self.current_step = step_id if status == StepStatus.RUNNING else None
        self.logger.info("Step status", step_id=step_id, status=status.value)

    def get_context(self) -> StateDict:
        """Get execution context for template resolution."""
        return {**self.params, **self.state, **{k: v for k, v in self.env.items()}}

    def update_from_tool_result(
        self, step_id: str, tool_result: StepResultDict
    ) -> None:
        """Update state from tool execution result."""
        validated_result = self._validate_state_values(tool_result)
        self.update(step_id, validated_result)

    def _validate_state_values(self, data: StepResultDict) -> StateDict:
        """Validate and convert data to StateValue types."""
        if not isinstance(data, dict):
            raise ValueError(f"Tool result must be a dict, got {type(data)}")

        validated = {}
        for key, value in data.items():
            if not isinstance(key, str):
                raise ValueError(f"State keys must be strings, got {type(key)}")

            validated[key] = self._validate_single_value(value)

        return validated

    def _validate_single_value(self, value: StateValue) -> StateValue:
        """Validate a single value as StateValue."""
        if isinstance(value, str | int | float | bool):
            return value
        elif isinstance(value, list):
            return [self._validate_single_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._validate_single_value(v) for k, v in value.items()}
        elif value is None:
            return value
        else:
            raise ValueError(f"Unsupported state value type: {type(value)}")

    def validate_step_outputs(
        self, step_config: StepConfig, outputs: StepResultDict
    ) -> bool:
        """Validate that outputs match step's writes declarations."""
        # Use StepConfig protocol to avoid circular imports
        if hasattr(step_config, "writes"):
            declared_outputs = set(step_config.writes)
            actual_outputs = set(outputs.keys())
            return declared_outputs.issubset(actual_outputs)
        return True  # If no writes declared, accept any outputs
