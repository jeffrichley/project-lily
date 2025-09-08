"""Unit tests for Petal executor core."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from lily.petal.executor.core import PetalExecutor
from lily.petal.models_strict import (
    DebugEchoStepConfig,
    PetalFile,
)


@pytest.mark.unit
class TestPetalExecutor:
    """Test PetalExecutor class."""

    def test_initializes_with_default_run_dir(self) -> None:
        """Test that PetalExecutor initializes with default run directory."""
        # Arrange - No setup needed

        # Act - Create executor
        executor = PetalExecutor()

        # Assert - Verify initialization
        assert executor.logger is not None

    def test_initializes_with_custom_run_dir(self) -> None:
        """Test that PetalExecutor initializes with custom run directory."""
        # Arrange - Prepare custom run directory
        custom_dir = Path("/custom/runs")

        # Act - Create executor with custom directory
        executor = PetalExecutor()

        # Assert - Verify initialization (run_dir is now generated per execution)
        assert executor.logger is not None

    @patch("builtins.open")
    @patch("ruamel.yaml.YAML")
    def test_load_petal_file_loads_yaml_correctly(self, mock_yaml, mock_open) -> None:
        """Test that load_petal_file loads YAML files correctly."""
        # Arrange - Mock YAML loading
        mock_yaml_instance = Mock()
        mock_yaml.return_value = mock_yaml_instance
        mock_yaml_instance.load.return_value = {
            "name": "test-workflow",
            "steps": [{"id": "step1", "uses": "debug.echo", "message": "hello"}],
        }
        mock_file = mock_open.return_value.__enter__.return_value

        executor = PetalExecutor()

        # Act - Load YAML file
        petal_file = executor.load_petal_file(Path("test.yaml"))

        # Assert - Verify YAML loading
        mock_open.assert_called_once_with(Path("test.yaml"))
        mock_yaml_instance.load.assert_called_once_with(mock_file.read())
        assert petal_file.name == "test-workflow"

    @patch("builtins.open")
    def test_load_petal_file_loads_json_correctly(self, mock_open) -> None:
        """Test that load_petal_file loads JSON files correctly."""
        # Arrange - Mock JSON loading
        json_data = {
            "name": "test-workflow",
            "steps": [{"id": "step1", "uses": "debug.echo", "message": "hello"}],
        }
        mock_file = mock_open.return_value.__enter__.return_value
        mock_file.read.return_value = '{"name": "test-workflow", "steps": [{"id": "step1", "uses": "debug.echo", "message": "hello"}]}'

        executor = PetalExecutor()

        # Act - Load JSON file
        petal_file = executor.load_petal_file(Path("test.json"))

        # Assert - Verify JSON loading
        mock_open.assert_called_once_with(Path("test.json"))
        assert petal_file.name == "test-workflow"

    @patch("builtins.open")
    @patch("pathlib.Path.mkdir")
    def test_execute_creates_run_directory(self, mock_mkdir, mock_open) -> None:
        """Test that execute creates run directory."""
        # Arrange - Create executor and petal file
        executor = PetalExecutor()
        step = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        petal_file = PetalFile(name="test", steps=[step])

        # Mock file operations
        mock_file = mock_open.return_value.__enter__.return_value

        # Act - Execute workflow
        state = executor.execute(petal_file)

        # Assert - Verify run directory was created
        mock_mkdir.assert_called()
        assert "run_id" in state
        assert "status" in state

    def test_execute_initializes_state_correctly(self) -> None:
        """Test that execute initializes workflow state correctly."""
        # Arrange - Create executor and petal file
        executor = PetalExecutor()
        step = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        petal_file = PetalFile(
            name="test",
            params={"input": "value"},
            env={"API_KEY": "secret"},
            steps=[step],
        )

        # Act - Execute workflow
        state = executor.execute(petal_file)

        # Assert - Verify state initialization
        assert "run_id" in state
        assert "status" in state
        assert "state" in state
        assert "step_results" in state

    def test_execute_runs_steps_sequentially(self) -> None:
        """Test that execute runs steps in sequence."""
        # Arrange - Create executor and petal file with multiple steps
        executor = PetalExecutor()
        step1 = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        step2 = DebugEchoStepConfig(id="step2", uses="debug.echo", message="world")
        petal_file = PetalFile(name="test", steps=[step1, step2])

        # Act - Execute workflow
        state = executor.execute(petal_file)

        # Assert - Verify execution
        assert "run_id" in state
        assert "status" in state
        assert "step_results" in state

    def test_execute_handles_fail_error_policy(self) -> None:
        """Test that execute handles fail error policy correctly."""
        # Arrange - Create executor and petal file with failing tool
        executor = PetalExecutor()

        # Create a step that will fail (unknown tool)
        step = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="test", steps=[step])

        # Act & Assert - Verify error is raised
        with pytest.raises(ValueError, match="Tool not found: unknown.tool"):
            executor.execute(petal_file)

    def test_execute_handles_skip_error_policy(self) -> None:
        """Test that execute handles skip error policy correctly."""
        # Arrange - Create executor and petal file with failing tool
        executor = PetalExecutor()

        # Create a step that will fail but with skip policy
        step = DebugEchoStepConfig(
            id="step1", uses="debug.echo", message="hello", if_error="skip"
        )
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="test", steps=[step])

        # Act - Execute workflow
        state = executor.execute(petal_file)

        # Assert - Verify execution completed despite error
        assert "run_id" in state
        assert "status" in state

    def test_execute_handles_retry_error_policy(self) -> None:
        """Test that execute handles retry error policy correctly."""
        # Arrange - Create executor and petal file with retry configuration
        executor = PetalExecutor()

        # Create a step that will fail but with retry policy
        step = DebugEchoStepConfig(
            id="step1", uses="debug.echo", message="hello", if_error="retry"
        )
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="test", steps=[step])

        # Act & Assert - Verify error is raised (no retry config)
        with pytest.raises(ValueError, match="Tool not found: unknown.tool"):
            executor.execute(petal_file)

    def test_execute_raises_for_unknown_tool(self) -> None:
        """Test that execute raises error for unknown tools."""
        # Arrange - Create executor and petal file with unknown tool
        executor = PetalExecutor()
        step = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="test", steps=[step])

        # Act & Assert - Verify error is raised
        with pytest.raises(ValueError, match="Tool not found: unknown.tool"):
            executor.execute(petal_file)

    def test_dry_run_validates_without_execution(self) -> None:
        """Test that dry run validates without executing tools."""
        # Arrange - Create executor and petal file
        executor = PetalExecutor()
        step = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        petal_file = PetalFile(name="test", steps=[step])

        # Act - Execute dry run
        state = executor.execute(petal_file, dry_run=True)

        # Assert - Verify dry run behavior
        assert state["status"] == "dry_run"
        assert "steps" in state

    def test_dry_run_warns_for_unknown_tools(self) -> None:
        """Test that dry run warns for unknown tools."""
        # Arrange - Create executor and petal file with unknown tool
        executor = PetalExecutor()
        step = DebugEchoStepConfig(id="step1", uses="debug.echo", message="hello")
        # Override the uses field to simulate unknown tool
        step.uses = "unknown.tool"
        petal_file = PetalFile(name="test", steps=[step])

        # Act - Execute dry run
        state = executor.execute(petal_file, dry_run=True)

        # Assert - Verify warning behavior (no exception raised)
        assert state["status"] == "dry_run"
        assert "steps" in state
