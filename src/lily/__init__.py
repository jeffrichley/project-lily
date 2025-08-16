"""Lily - Software development project planning and organization tool."""

__version__ = "1.0.0"

from lily.cli import app

# Petal workflow system
from lily.petal import IfErrorPolicy, StepStatus
from lily.petal.executor import PetalExecutor, ToolContext, WorkflowState
from lily.petal.models_strict import PetalFile, Retry, StepConfig

__all__ = [
    "__version__",
    "app",
    # Petal exports
    "PetalFile",
    "Retry",
    "StepConfig",
    "IfErrorPolicy",
    "StepStatus",
    # Petal executor exports
    "PetalExecutor",
    "ToolContext",
    "WorkflowState",
]
