"""Enums for Petal workflow system."""

from enum import Enum


class IfErrorPolicy(str, Enum):
    """Error handling policies for steps."""

    FAIL = "fail"
    SKIP = "skip"
    RETRY = "retry"


class StepStatus(str, Enum):
    """Execution status of a step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"
