"""Unit tests for Petal executor tools."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from lily.petal.executor.tools import ToolContext
from lily.petal.tool_registry import tool_registry


@pytest.mark.unit
class TestToolContext:
    """Test ToolContext class."""

    def test_initializes_with_correct_values(self) -> None:
        """Test that ToolContext initializes with correct values."""
        # Arrange - Prepare test data
        from lily.petal.executor.state import WorkflowState

        state = WorkflowState(
            run_id="test", run_dir=Path("/tmp/runs"), params={}, env={}
        )
        run_dir = "/tmp/runs"
        env = {"API_KEY": "secret"}

        # Act - Create tool context
        context = ToolContext(state, run_dir, env)

        # Assert - Verify initialization
        assert context.state == state
        assert context.run_dir == run_dir
        assert context.env == env
        assert context.logger is not None


@pytest.mark.unit
class TestToolRegistry:
    """Test ToolRegistry class."""

    def test_initializes_with_builtin_tools(self) -> None:
        """Test that ToolRegistry initializes with built-in tools."""
        # Arrange - No setup needed

        # Act - Use global tool registry
        tools = tool_registry.list_tools()

        # Assert - Verify built-in tools are registered
        assert "debug.echo" in tools
        assert "python.eval" in tools
        assert len(tools) >= 2  # At least the built-in tools

    def test_registers_custom_tool(self) -> None:
        """Test that register_tool method adds custom tools."""
        # Arrange - Create mock tool
        mock_tool = Mock()
        mock_tool.name = "custom.tool"
        mock_tool.step_config_class = Mock()
        mock_tool.step_config_class.__name__ = "MockStepConfig"
        mock_tool.get_description.return_value = "Test tool"

        # Act - Register custom tool
        tool_registry.register_tool(mock_tool)

        # Assert - Verify tool is registered
        assert "custom.tool" in tool_registry.list_tools()
        assert tool_registry.get_tool("custom.tool") == mock_tool

    def test_get_tool_returns_none_for_unknown_tool(self) -> None:
        """Test that get_tool returns None for unknown tools."""
        # Arrange - No setup needed

        # Act - Get unknown tool
        tool = tool_registry.get_tool("unknown.tool")

        # Assert - Verify None is returned
        assert tool is None

    def test_validate_step_with_valid_tool(self) -> None:
        """Test that validate_step works with valid tools."""
        # Arrange - Create mock step
        mock_step = Mock()
        mock_step.uses = "debug.echo"

        # Act - Validate step
        is_valid = tool_registry.validate_step(mock_step)

        # Assert - Verify step is valid
        assert is_valid is True

    def test_validate_step_with_invalid_tool(self) -> None:
        """Test that validate_step works with invalid tools."""
        # Arrange - Create mock step
        mock_step = Mock()
        mock_step.uses = "unknown.tool"

        # Act - Validate step
        is_valid = tool_registry.validate_step(mock_step)

        # Assert - Verify step is invalid
        assert is_valid is False
