"""Tool registry for Petal workflow system."""

import structlog

from lily.petal.executor.tools import ToolContext
from lily.petal.executor.types import StepConfig, StepResultDict
from lily.petal.tool_protocol import Tool

# Try to import tools for auto-discovery
try:
    from lily.petal.tools import (
        DebugEchoTool,
        PythonEvalTool,
    )

    _TOOLS_AVAILABLE = True
except ImportError:
    _TOOLS_AVAILABLE = False


class ToolRegistry:
    """Registry for Petal tools using the Tool protocol."""

    def __init__(self) -> None:
        """Initialize tool registry."""
        self._tools: dict[str, Tool] = {}
        self._step_config_classes: dict[str, type[StepConfig]] = {}
        self.logger = structlog.get_logger()

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the registry."""
        tool_name = tool.name
        step_config_class = tool.step_config_class

        self._tools[tool_name] = tool
        self._step_config_classes[tool_name] = step_config_class

        self.logger.info(
            "Registered tool",
            tool_name=tool_name,
            step_config_class=step_config_class.__name__,
            description=tool.get_description(),
        )

    def get_tool(self, tool_name: str) -> Tool | None:
        """Get a tool by name."""
        return self._tools.get(tool_name)

    def get_step_config_class(self, tool_name: str) -> type[StepConfig] | None:
        """Get the step config class for a tool."""
        return self._step_config_classes.get(tool_name)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def validate_step(self, step: StepConfig) -> bool:
        """Validate that a step has a registered tool and valid configuration."""
        tool_name = step.uses
        tool = self.get_tool(tool_name)

        if not tool:
            self.logger.error("Tool not found", tool_name=tool_name)
            return False

        # Delegate validation to the tool
        return tool.validate(step)

    def execute_step(self, ctx: ToolContext, step: StepConfig) -> StepResultDict:
        """Execute a step using its registered tool."""
        tool_name = step.uses
        tool = self.get_tool(tool_name)

        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")

        # Execute the tool
        result = tool.execute(ctx, step)

        # Validate result against step config
        if (
            hasattr(ctx, "state")
            and hasattr(ctx.state, "validate_step_outputs")
            and not ctx.state.validate_step_outputs(step, result)
        ):
            raise ValueError(f"Tool outputs don't match step writes: {step.id}")

        return result


# Global tool registry instance
tool_registry = ToolRegistry()


# Decorator for easy tool registration
def register_tool(tool: Tool) -> Tool:
    """Decorator to register a tool with the global registry."""
    tool_registry.register_tool(tool)
    return tool


# Convenience function for registering custom tools
def register_custom_tool(tool: Tool) -> None:
    """Register a custom tool with the global registry."""
    tool_registry.register_tool(tool)


# Auto-discover and register tools from the tools package
def _auto_discover_tools() -> None:
    """Auto-discover and register tools from the tools package."""
    if _TOOLS_AVAILABLE:
        # Register discovered tools by creating instances
        tool_registry.register_tool(DebugEchoTool())
        tool_registry.register_tool(PythonEvalTool())
    else:
        # Tools package might not be available during development
        tool_registry.logger.warning("Tools package not available for auto-discovery")


# Auto-discover tools on module import
_auto_discover_tools()
