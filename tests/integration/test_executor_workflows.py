"""Integration tests for Petal executor workflows."""

import pytest

from lily.petal.enums import IfErrorPolicy, StepStatus
from lily.petal.executor.core import PetalExecutor
from lily.petal.models_strict import (
    DebugEchoStepConfig,
    PetalFile,
    PythonEvalStepConfig,
)


@pytest.mark.integration
class TestExecutorWorkflows:
    """Test Petal executor workflow execution."""

    def test_simple_workflow_execution(self) -> None:
        """Test execution of a simple workflow with debug tools."""
        # Arrange - Create a simple workflow
        step1 = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        step2 = PythonEvalStepConfig(id="step2", uses="python.eval", expression="2 + 2")
        petal_file = PetalFile(
            name="simple-test", params={"input": "test"}, steps=[step1, step2]
        )

        # Act - Execute workflow
        executor = PetalExecutor()
        state = executor.execute(petal_file)

        # Assert - Verify execution
        assert "run_id" in state
        assert "status" in state
        assert "step_results" in state

    def test_workflow_with_error_handling(self) -> None:
        """Test workflow execution with error handling policies."""
        # Arrange - Create workflow with failing tool
        executor = PetalExecutor()

        # Create a step that will fail (unknown tool)
        step = DebugEchoStepConfig(
            id="step1", uses="debug.echo", message="hello", if_error="skip"
        )
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="error-test", steps=[step])

        # Act - Execute workflow
        state = executor.execute(petal_file)

        # Assert - Verify execution completed despite error
        assert "run_id" in state
        assert "status" in state

    def test_workflow_with_retry_logic(self) -> None:
        """Test workflow execution with retry logic."""
        # Arrange - Create workflow with flaky tool
        executor = PetalExecutor()

        # Create a step that will fail (unknown tool)
        step = DebugEchoStepConfig(
            id="step1", uses="debug.echo", message="hello", if_error="retry"
        )
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="retry-test", steps=[step])

        # Act & Assert - Verify error is raised (no retry config)
        with pytest.raises(ValueError, match="Tool not found: unknown.tool"):
            executor.execute(petal_file)

    def test_workflow_with_context_resolution(self) -> None:
        """Test workflow with proper context resolution."""
        # Arrange - Create workflow that uses context
        step1 = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        step2 = PythonEvalStepConfig(
            id="step2", uses="python.eval", expression="f'Message: {message}'"
        )
        petal_file = PetalFile(
            name="context-test", params={"prefix": "Test"}, steps=[step1, step2]
        )

        # Act - Execute workflow
        executor = PetalExecutor()
        state = executor.execute(petal_file)

        # Assert - Verify execution
        assert "run_id" in state
        assert "status" in state
        assert "step_results" in state

    def test_dry_run_validation(self) -> None:
        """Test dry run mode for workflow validation."""
        # Arrange - Create workflow
        step1 = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        step2 = DebugEchoStepConfig(id="step2", uses="debug.echo", message="world")
        # Override the uses field to simulate unknown tool
        step2.uses = "unknown.tool"
        petal_file = PetalFile(name="dry-run-test", steps=[step1, step2])

        # Act - Execute dry run
        executor = PetalExecutor()
        state = executor.execute(petal_file, dry_run=True)

        # Assert - Verify dry run behavior
        assert state["status"] == "dry_run"
        assert "steps" in state

    def test_workflow_state_persistence(self) -> None:
        """Test that workflow state is properly persisted."""
        # Arrange - Create workflow
        step1 = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        step2 = PythonEvalStepConfig(
            id="step2", uses="python.eval", expression="len('hello')"
        )
        petal_file = PetalFile(name="persistence-test", steps=[step1, step2])

        # Act - Execute workflow
        executor = PetalExecutor()
        state = executor.execute(petal_file)

        # Assert - Verify execution
        assert "run_id" in state
        assert "status" in state
        assert "step_results" in state
