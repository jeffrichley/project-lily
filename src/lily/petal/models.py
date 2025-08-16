"""Canonical Pydantic models for Petal workflow system."""

from typing import Any

from pydantic import BaseModel, Field, field_validator

from lily.petal.enums import IfErrorPolicy


class Retry(BaseModel):
    """Retry configuration for steps."""

    max_attempts: int = Field(gt=0, description="Maximum number of retry attempts")
    backoff_factor: float = Field(
        default=1.5, gt=0, description="Exponential backoff multiplier"
    )
    jitter: bool = Field(
        default=True, description="Add random jitter to backoff delays"
    )
    max_delay: float | None = Field(
        default=None, gt=0, description="Maximum delay between retries in seconds"
    )


class Step(BaseModel):
    """A single step in a Petal workflow."""

    id: str = Field(description="Unique identifier for the step")
    uses: str = Field(description="Tool name to execute")
    reads: list[str] = Field(
        default_factory=list, description="Input dependencies from state/params"
    )
    writes: list[str] = Field(default_factory=list, description="Output declarations")
    with_: dict[str, Any] = Field(
        default_factory=dict, alias="with", description="Tool input parameters"
    )
    when: str | None = Field(
        default=None, description="Jinja condition for step execution"
    )
    if_error: IfErrorPolicy = Field(
        default=IfErrorPolicy.FAIL, description="Error handling policy"
    )
    retry: Retry | None = Field(
        default=None, description="Step-specific retry configuration"
    )

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate step ID format."""
        if not v or not v.strip():
            raise ValueError("Step ID cannot be empty")
        if " " in v:
            raise ValueError("Step ID cannot contain spaces")
        return v.strip()

    @field_validator("uses")
    @classmethod
    def validate_uses(cls, v: str) -> str:
        """Validate tool name format."""
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
    }


class PetalFile(BaseModel):
    """Canonical representation of a Petal workflow file."""

    version: str = Field(default="0.1", description="Petal file format version")
    name: str = Field(description="Workflow name")
    description: str | None = Field(default=None, description="Workflow description")
    params: dict[str, Any] = Field(
        default_factory=dict, description="User-supplied parameters"
    )
    defaults: dict[str, Any] = Field(
        default_factory=dict, description="Global defaults for tools"
    )
    env: dict[str, str] = Field(
        default_factory=dict, description="Environment variable mapping"
    )
    secrets: list[str] = Field(
        default_factory=list, description="Secret names to resolve at runtime"
    )
    macros: dict[str, list[dict[str, Any]]] = Field(
        default_factory=dict, description="Reusable step groups"
    )
    imports: list[dict[str, str]] = Field(
        default_factory=list, description="Include files or packages"
    )
    steps: list[Step] = Field(description="Ordered list of execution steps")

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        if not v or not v.strip():
            raise ValueError("Version cannot be empty")
        return v.strip()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate workflow name."""
        if not v or not v.strip():
            raise ValueError("Workflow name cannot be empty")
        if " " in v:
            raise ValueError("Workflow name cannot contain spaces")
        return v.strip()

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: list[Step]) -> list[Step]:
        """Validate steps list."""
        if not v:
            raise ValueError("At least one step is required")
        return v

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
    }
