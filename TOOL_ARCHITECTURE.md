# Petal Tool Architecture with Tool Protocol

## Overview

The Petal tool system uses a clean, type-safe architecture where **tools are the entry point** and encapsulate both their data schema and implementation logic. The system uses **Protocols** for maximum flexibility and ease of use.

## Architecture Components

### 1. Tool Protocol
The foundation of the tool system - every tool must implement this protocol:

```python
@runtime_checkable
class Tool(Protocol):
    @property
    def name(self) -> str:
        """The name of the tool (e.g., 'debug.echo')."""
        ...
    
    @property
    def step_config_class(self) -> Type[StepConfig]:
        """The Pydantic step config class for this tool's configuration."""
        ...
    
    def execute(self, ctx: ToolContext, step: StepConfig) -> Dict[str, Any]:
        """Execute the tool with the given context and step configuration."""
        ...
    
    def validate(self, step: StepConfig) -> bool:
        """Validate that the step configuration is correct for this tool."""
        return step.uses == self.name
    
    def get_description(self) -> str:
        """Get a description of what this tool does."""
        return "Tool description"
```

### 2. Individual Tool Files
Each tool is self-contained in its own file with both step config and implementation:

```python
# src/lily/petal/tools/debug_echo.py
class DebugEchoStepConfig(StepConfig):
    """Configuration for debug.echo tool."""
    uses: Literal["debug.echo"]
    message: str
    level: Literal["debug", "info", "warning", "error"]

class DebugEchoTool:
    """Tool for echoing debug messages."""
    @property
    def name(self) -> str: return "debug.echo"
    @property
    def step_config_class(self): return DebugEchoStepConfig
    # ... implementation
```

### 3. Strongly Typed Returns
Tools can define strongly typed return types using TypedDict:

```python
class PythonEvalSuccess(TypedDict):
    """Successful evaluation result."""
    result: Any
    expression: str

class PythonEvalError(TypedDict):
    """Error evaluation result."""
    error: str
    expression: str

PythonEvalResult = Union[PythonEvalSuccess, PythonEvalError]

def execute(self, ctx: ToolContext, step: StepConfig) -> PythonEvalResult:
    # Implementation with type-safe returns
```

### 4. Tool Registry with Auto-Discovery
Manages all registered tools and auto-discovers them:

```python
class ToolRegistry:
    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the registry."""
    
    def get_tool(self, tool_name: str) -> Tool | None:
        """Get a tool by name."""
    
    def validate_step(self, step: StepConfig) -> bool:
        """Validate that a step has a registered tool and valid configuration."""
        # Delegates to tool.validate()
    
    def execute_step(self, ctx: Any, step: StepConfig) -> Dict[str, Any]:
        """Execute a step using its registered tool."""
        # Delegates to tool.execute()

# Auto-discovery on module import
def _auto_discover_tools() -> None:
    from lily.petal.tools import DebugEchoTool, PythonEvalTool
    register_tool(DebugEchoTool())
    register_tool(PythonEvalTool())

_auto_discover_tools()
```

## Key Benefits

### 1. **Clean Separation of Concerns**
- `tool_protocol.py` - Only contains the protocol definition
- Individual tool files - Self-contained with config and implementation
- No circular imports or hardwired dependencies

### 2. **Strongly Typed Returns**
- Tools can define TypedDict return types
- Compile-time validation of return values
- Clear success/error handling patterns

### 3. **Auto-Discovery**
- Tools register themselves automatically
- No manual registration required
- Easy to add new tools

### 4. **Modular Structure**
- Each tool in its own file
- Step config and tool implementation together
- Easy to maintain and extend

### 5. **Protocol-Based Design**
- No inheritance required - just implement the required methods
- Any class with the right methods works
- Easier to test with mocks
- More flexible for existing classes

### 6. **Clear Naming**
- `StepConfig` - Clear that this is configuration for a step
- `Tool` - Simple, clean name for the execution protocol
- `step_config_class` - Clear relationship between tool and config
- No 'Protocol' in name - Less verbose

## Example: Adding a New Tool

### Step 1: Create the Tool File
```python
# src/lily/petal/tools/database_query.py
from typing import TypedDict, Union
from pydantic import Field

class DatabaseQueryStepConfig(StepConfig):
    uses: Literal["database.query"]
    query: str = Field(description="SQL query to execute")
    connection_string: str = Field(description="Database connection string")

class DatabaseQuerySuccess(TypedDict):
    rows: list[dict]
    count: int

class DatabaseQueryError(TypedDict):
    error: str
    query: str

DatabaseQueryResult = Union[DatabaseQuerySuccess, DatabaseQueryError]

class DatabaseQueryTool:
    @property
    def name(self) -> str: return "database.query"
    @property
    def step_config_class(self): return DatabaseQueryStepConfig
    
    def execute(self, ctx: ToolContext, step: StepConfig) -> DatabaseQueryResult:
        # Implementation with type-safe returns
        return {"rows": result_rows, "count": len(result_rows)}
```

### Step 2: Add to Tools Package
```python
# src/lily/petal/tools/__init__.py
from .database_query import DatabaseQueryTool, DatabaseQueryStepConfig

__all__ = [
    # ... existing tools ...
    "DatabaseQueryTool",
    "DatabaseQueryStepConfig",
]
```

### Step 3: Auto-Registration
The tool is automatically registered when the module is imported!

## Usage in YAML

```yaml
steps:
  - id: "query-users"
    uses: "database.query"
    query: "SELECT * FROM users WHERE active = true"
    connection_string: "postgresql://user:pass@localhost/db"
```

## Architecture Flow

```
YAML File (steps)
    ↓
PetalFile (Pydantic model)
    ↓
StepConfig (Discriminated union of step config types)
    ↓
Tool Registry (Auto-discovered)
    ↓
Tool (Protocol implementation)
    ↓
Execute with type-safe access to step fields and returns
```

## Domain Model

**Clear separation of concerns:**
- **YAML** has `steps` (user-defined workflow steps)
- **StepConfig** = Configuration/schema for a step
- **Tool** = Execution engine for a step
- **Tool Registry** = Connects tools to step configs

**Relationship:**
- A **Step** in YAML references a **Tool** via `uses: "tool.name"`
- The **Tool** provides the **StepConfig** class for validation
- The **Tool** executes the step using the **StepConfig** data
- The **Tool** returns strongly typed results

## File Structure

```
src/lily/petal/
├── tool_protocol.py          # Clean protocol definition only
├── tool_registry.py          # Auto-discovery and registration
├── models_strict.py          # Base models and PetalFile
└── tools/                    # Individual tool files
    ├── __init__.py           # Tool exports
    ├── debug_echo.py         # Debug echo tool + config
    ├── python_eval.py        # Python eval tool + config
    └── database_query.py     # Database query tool + config
```

## Benefits Summary

1. **Better Developer Experience**
   - IDE autocomplete for all tool fields and returns
   - Compile-time validation
   - Clear error messages
   - No inheritance required

2. **Better User Experience**
   - Type-safe YAML configuration
   - Validation at multiple levels
   - Self-documenting tools

3. **Better Maintainability**
   - Tools are self-contained in individual files
   - Easy to add new tools
   - Clear separation of concerns
   - Protocol-based design

4. **Better Reliability**
   - Type safety throughout
   - Runtime validation
   - Delegated responsibility
   - Duck typing support

5. **Better Organization**
   - Clean tool_protocol.py
   - Step configs and tools together
   - Auto-discovery
   - Modular structure

This architecture transforms Petal into a truly extensible, type-safe workflow system where tools are first-class citizens with complete control over their configuration and execution, using the flexibility of Protocols for maximum developer convenience.
