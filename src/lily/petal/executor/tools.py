"""Tool context for Petal executor."""

import structlog

from lily.petal.executor.state import WorkflowState


class ToolContext:
    """Context provided to tools during execution."""

    def __init__(self, state: WorkflowState, run_dir: str, env: dict[str, str]) -> None:
        """Initialize tool context."""
        self.state = state
        self.run_dir = run_dir
        self.env = env
        self.logger = structlog.get_logger()
