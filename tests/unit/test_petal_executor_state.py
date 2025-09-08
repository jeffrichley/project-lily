"""Unit tests for Petal executor state."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from lily.petal.enums import StepStatus
from lily.petal.executor.state import WorkflowState


@pytest.mark.unit
class TestWorkflowState:
    """Test WorkflowState class."""

    def test_initializes_with_correct_values(self) -> None:
        """Test that WorkflowState initializes with correct values."""
        # Arrange - Prepare test data
        run_id = "test-run-123"
        run_dir = Path("/tmp/test")
        params = {"input": "value"}
        env = {"API_KEY": "secret"}

        # Act - Create workflow state
        state = WorkflowState(run_id, run_dir, params, env)

        # Assert - Verify initialization
        assert state.run_id == run_id
        assert state.run_dir == run_dir
        assert state.params == params
        assert state.env == env
        assert state.state == {}
        assert state.step_status == {}
        assert state.step_results == {}

    def test_sets_step_status_correctly(self) -> None:
        """Test that set_step_status updates step status and current step."""
        # Arrange - Create state
        state = WorkflowState("test", Path("/tmp"), {}, {})
        step_id = "step-1"

        # Act - Set step status to running
        state.set_step_status(step_id, StepStatus.RUNNING)

        # Assert - Verify status was set
        assert state.step_status[step_id] == StepStatus.RUNNING
        assert state.current_step == step_id

    def test_updates_state_with_step_outputs(self) -> None:
        """Test that update method correctly merges step outputs."""
        # Arrange - Create state and step outputs
        state = WorkflowState("test", Path("/tmp"), {}, {})
        step_id = "step-1"
        outputs = {"result": "success", "count": 42}

        # Act - Update state with outputs
        state.update_from_tool_result(step_id, outputs)

        # Assert - Verify state was updated correctly
        assert state.state == outputs
        assert state.step_results[step_id] == outputs

    def test_merges_multiple_step_outputs(self) -> None:
        """Test that multiple step outputs are merged correctly."""
        # Arrange - Create state
        state = WorkflowState("test", Path("/tmp"), {}, {})

        # Act - Update state with multiple step outputs
        state.update_from_tool_result("step1", {"a": 1, "b": 2})
        state.update_from_tool_result("step2", {"c": 3, "d": 4})

        # Assert - Verify outputs were merged
        assert state.state == {"a": 1, "b": 2, "c": 3, "d": 4}
        assert state.step_results["step1"] == {"a": 1, "b": 2}
        assert state.step_results["step2"] == {"c": 3, "d": 4}

    def test_handles_overlapping_output_keys(self) -> None:
        """Test that overlapping output keys are handled correctly."""
        # Arrange - Create state
        state = WorkflowState("test", Path("/tmp"), {}, {})

        # Act - Update state with overlapping keys
        state.update_from_tool_result("step1", {"key": "value1"})
        state.update_from_tool_result("step2", {"key": "value2"})

        # Assert - Verify later step overwrites earlier step
        assert state.state == {"key": "value2"}
        assert state.step_results["step1"] == {"key": "value1"}
        assert state.step_results["step2"] == {"key": "value2"}

    def test_validates_state_values(self) -> None:
        """Test that state values are validated correctly."""
        # Arrange - Create state
        state = WorkflowState("test", Path("/tmp"), {}, {})

        # Act & Assert - Test valid values
        valid_outputs = {
            "string": "hello",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"},
        }
        state.update_from_tool_result("step1", valid_outputs)
        assert state.state == valid_outputs

    def test_handles_empty_outputs(self) -> None:
        """Test that empty outputs are handled correctly."""
        # Arrange - Create state
        state = WorkflowState("test", Path("/tmp"), {}, {})

        # Act - Update state with empty outputs
        state.update_from_tool_result("step1", {})

        # Assert - Verify empty outputs are handled
        assert state.state == {}
        assert state.step_results["step1"] == {}

    def test_get_context_returns_correct_structure(self) -> None:
        """Test that get_context returns the correct context structure."""
        # Arrange - Create state with some data
        state = WorkflowState("test", Path("/tmp"), {"param": "value"}, {"ENV": "test"})
        state.state = {"result": "success"}

        # Act - Get context
        context = state.get_context()

        # Assert - Verify context structure
        assert "param" in context
        assert "ENV" in context
        assert "result" in context
        assert context["param"] == "value"
        assert context["ENV"] == "test"
        assert context["result"] == "success"

    def test_validate_step_outputs_with_matching_writes(self) -> None:
        """Test that validate_step_outputs works with matching writes."""
        # Arrange - Create state and step config
        state = WorkflowState("test", Path("/tmp"), {}, {})
        step_config = Mock()
        step_config.writes = ["result", "count"]
        outputs = {"result": "success", "count": 42}

        # Act - Validate outputs
        is_valid = state.validate_step_outputs(step_config, outputs)

        # Assert - Verify validation passed
        assert is_valid is True

    def test_validate_step_outputs_with_missing_writes(self) -> None:
        """Test that validate_step_outputs fails with missing writes."""
        # Arrange - Create state and step config
        state = WorkflowState("test", Path("/tmp"), {}, {})
        step_config = Mock()
        step_config.writes = ["result", "count", "missing"]
        outputs = {"result": "success", "count": 42}

        # Act - Validate outputs
        is_valid = state.validate_step_outputs(step_config, outputs)

        # Assert - Verify validation failed
        assert is_valid is False

    def test_validate_step_outputs_with_extra_outputs(self) -> None:
        """Test that validate_step_outputs passes with extra outputs."""
        # Arrange - Create state and step config
        state = WorkflowState("test", Path("/tmp"), {}, {})
        step_config = Mock()
        step_config.writes = ["result"]
        outputs = {"result": "success", "extra": "value"}

        # Act - Validate outputs
        is_valid = state.validate_step_outputs(step_config, outputs)

        # Assert - Verify validation passed (extra outputs are allowed)
        assert is_valid is True
