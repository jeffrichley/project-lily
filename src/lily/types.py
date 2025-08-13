"""Centralized type definitions for the Lily project."""

from typing import Literal

# Simple JSON-like types using PEP 695 type aliases (Python 3.12+)
type JsonValue = str | int | float | bool | None | list[JsonValue] | dict[
    str, JsonValue
]

# Template context values using PEP 695 type aliases
type TemplateValue = (
    str | int | float | bool | list[TemplateValue] | dict[str, TemplateValue] | None
)

# YAML data types - same as JsonValue since they're essentially the same
YamlValue = JsonValue

# Resource and configuration types
ResourceValue = str | int | float | bool
ResourceDict = dict[str, ResourceValue]

# Cache policy types
CachePolicy = str | Literal["auto", "never", "read-only", "write-only"]
CacheDict = dict[str, CachePolicy]

# Retry configuration types
RetryDict = dict[
    str, int | str
]  # max: int, backoff: str (time format like "30s", "2m")

# With clause types - simplified
WithDict = dict[
    str, str | int | float | bool | list[str] | dict[str, str | int | float | bool]
]

# Step input/output types
StepIODict = dict[str, str | int | float | bool]

# Artifacts types
ArtifactsDict = dict[str, str | int | float | bool | list[str]]

# Lock file types
LockFileDict = dict[str, JsonValue]
