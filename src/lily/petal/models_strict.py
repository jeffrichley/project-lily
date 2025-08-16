"""Strictly typed Pydantic models for Petal workflow system."""

from typing import Literal

from pydantic import BaseModel, Field


class Retry(BaseModel):
    """Retry configuration for a step."""

    max_attempts: int = Field(ge=1, le=10, description="Maximum number of attempts")
    backoff_factor: float = Field(ge=0.1, le=10.0, description="Backoff multiplier")
    max_delay: float = Field(
        ge=1.0, le=3600.0, description="Maximum delay between attempts"
    )


class BaseStepConfig(BaseModel):
    """Base configuration for all steps."""

    id: str = Field(description="Unique identifier for the step")
    uses: str = Field(description="Tool to use for this step")
    reads: list[str] = Field(
        default_factory=list, description="Input variables this step reads"
    )
    writes: list[str] = Field(
        default_factory=list, description="Output variables this step writes"
    )
    when: str | None = Field(
        default=None, description="Condition for when to execute this step"
    )
    if_error: str = Field(default="fail", description="Error handling policy")
    retry: Retry | None = Field(default=None, description="Retry configuration")
    with_: dict[str, str] = Field(
        default_factory=dict, alias="with", description="Tool-specific parameters"
    )


class DebugEchoStepConfig(BaseStepConfig):
    """Configuration for debug.echo tool."""

    uses: Literal["debug.echo"]
    message: str = Field(description="Message to echo")
    timestamp: str | None = Field(default=None, description="Optional timestamp")
    level: Literal["debug", "info", "warning", "error"] = Field(
        default="info", description="Log level"
    )


class PythonEvalStepConfig(BaseStepConfig):
    """Configuration for python.eval tool."""

    uses: Literal["python.eval"]
    expression: str = Field(description="Python expression to evaluate")
    globals: dict[str, str] = Field(
        default_factory=dict, description="Global variables for evaluation"
    )
    locals: dict[str, str] = Field(
        default_factory=dict, description="Local variables for evaluation"
    )


# Union type for all step configs
StepConfig = DebugEchoStepConfig | PythonEvalStepConfig


class PetalFile(BaseModel):
    """Complete Petal workflow file."""

    name: str = Field(description="Name of the workflow")
    description: str | None = Field(
        default=None, description="Description of the workflow"
    )
    version: str = Field(default="0.1", description="Version of the workflow")
    params: dict[str, str | int | float | bool] = Field(
        default_factory=dict, description="Workflow parameters"
    )
    env: dict[str, str] = Field(
        default_factory=dict, description="Environment variables"
    )
    steps: list[StepConfig] = Field(description="List of steps to execute")
