"""Debug echo tool for Petal workflow system."""

from lily.petal.executor.tools import ToolContext
from lily.petal.executor.types import StepResultDict
from lily.petal.models_strict import DebugEchoStepConfig


class DebugEchoTool:
    """Tool for echoing debug messages."""

    @property
    def name(self) -> str:
        """Get the tool name."""
        return "debug.echo"

    @property
    def step_config_class(self) -> type[DebugEchoStepConfig]:
        """Get the step config class for this tool."""
        return DebugEchoStepConfig

    def get_description(self) -> str:
        """Get a description of what this tool does."""
        return "Tool for echoing debug messages."

    def validate(self, step: DebugEchoStepConfig) -> bool:
        """Validate that the step configuration is correct for this tool."""
        return step.uses == self.name

    def execute(self, ctx: ToolContext, step: DebugEchoStepConfig) -> StepResultDict:
        """Execute the tool with the given context and step configuration."""
        message = step.message
        level = step.level
        timestamp = step.timestamp

        # Log the message
        if level == "debug":
            ctx.logger.debug(message, timestamp=timestamp)
        elif level == "info":
            ctx.logger.info(message, timestamp=timestamp)
        elif level == "warning":
            ctx.logger.warning(message, timestamp=timestamp)
        elif level == "error":
            ctx.logger.error(message, timestamp=timestamp)

        return {
            "message": message,
            "level": level,
            "timestamp": timestamp,
            "logged": True,
        }
