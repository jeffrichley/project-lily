"""Type definitions for Lily."""

from typing import Any

# JSON value types
JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]

# Configuration types
ConfigDict = dict[str, JsonValue]

# Runtime overrides
RuntimeOverrides = dict[str, Any]

# Theme types
ThemeConfig = dict[str, Any]
ColorScheme = dict[str, str]

# File types
FilePath = str
DirectoryPath = str

# Environment types
EnvironmentVariables = dict[str, str]

# Logging types
LogLevel = str
LogMessage = str
