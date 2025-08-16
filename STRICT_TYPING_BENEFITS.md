# Strict Typing Benefits for Petal System

## Overview

The strictly typed Petal models provide significant improvements over the current generic approach. Here's a comprehensive comparison and migration guide.

## Current vs Strictly Typed Approach

### Current Approach (Generic)
```python
# Current models.py
class Step(BaseModel):
    id: str
    uses: str  # Generic string - no validation
    with_: dict[str, object] = Field(alias="with")  # Generic dict with object
```

**Problems:**
- ❌ No tool-specific field validation
- ❌ No IDE autocomplete for tool fields
- ❌ Runtime errors for invalid tool configurations
- ❌ Difficult to add new tools
- ❌ No type safety for tool parameters

### Strictly Typed Approach
```python
# New models_strict.py
@register_tool
class DebugEchoStep(BaseStep):
    uses: Literal["debug.echo"]
    message: str
    level: Literal["debug", "info", "warning", "error"]
    timestamp: str | None

@register_tool
class PythonEvalStep(BaseStep):
    uses: Literal["python.eval"]
    expression: str
    globals: dict[str, str]
    locals: dict[str, str]
```

**Benefits:**
- ✅ Tool-specific field validation
- ✅ IDE autocomplete for all tool fields
- ✅ Compile-time type checking
- ✅ Easy to add new tools with decorator
- ✅ Runtime validation ensures correct data types

## Key Features

### 1. **Tool Registration System**
```python
@register_tool
class MyCustomStep(BaseStep):
    uses: Literal["my.custom.tool"]
    tool_name: ClassVar[str] = "my.custom.tool"
    # Tool-specific fields...
```

### 2. **Discriminated Unions**
```python
# Automatically creates union of all registered tools
StepUnion = Union[tuple(TOOL_REGISTRY.values())]
```

### 3. **Type-Safe Tool Access**
```python
def get_step_class(tool_name: str) -> type[BaseStep] | None:
    return TOOL_REGISTRY.get(tool_name)

# Usage
step_class = get_step_class("debug.echo")  # Returns DebugEchoStep
```

### 4. **Strict Field Validation**
```python
# Only valid HTTP methods allowed
method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

# Only valid log levels allowed
level: Literal["debug", "info", "warning", "error"]

# Required fields with proper types
expression: str  # Must be string, not any JSON value
```

## Migration Benefits

### For Developers

1. **IDE Support**
   ```python
   # Before: No autocomplete for tool fields
   step.with_["message"] = "Hello"  # No type hints
   
   # After: Full autocomplete and type hints
   step.message = "Hello"  # IDE knows this is a string
   step.level = "info"     # IDE suggests valid options
   ```

2. **Compile-Time Validation**
   ```python
   # Before: Runtime error only
   step.with_["level"] = "invalid_level"  # Fails at runtime
   
   # After: Compile-time error
   step.level = "invalid_level"  # Type checker catches this
   ```

3. **Easy Tool Addition**
   ```python
   # Just add a new class with decorator
   @register_tool
   class DatabaseStep(BaseStep):
       uses: Literal["database.query"]
       query: str
       connection_string: str
   ```

### For Users

1. **Better Error Messages**
   ```yaml
   # Before: Generic error
   steps:
     - id: "test"
       uses: "debug.echo"
       with:
         level: "invalid"  # Runtime error: "invalid value"
   
   # After: Specific error
   steps:
     - id: "test"
       uses: "debug.echo"
       level: "invalid"  # Validation error: "must be one of: debug, info, warning, error"
   ```

2. **Documentation in Code**
   ```python
   # Field descriptions are part of the model
   message: str = Field(description="Message to echo")
   level: Literal["debug", "info", "warning", "error"] = Field(
       default="info", description="Log level"
   )
   ```

## Implementation Strategy

### Phase 1: Create Strict Models (✅ Done)
- [x] Create `models_strict.py` with tool-specific classes
- [x] Implement tool registration system
- [x] Add discriminated unions

### Phase 2: Update Executor
- [ ] Modify executor to use strict models
- [ ] Update tool registry to work with strict types
- [ ] Add runtime type checking

### Phase 3: Migration
- [ ] Update existing `.petal` files to use strict syntax
- [ ] Add migration tools for existing workflows
- [ ] Update documentation

### Phase 4: Enhanced Features
- [ ] Add JSON Schema generation for LSP
- [ ] Add validation rules for tool combinations
- [ ] Add custom validators for complex fields

## Example Usage

### YAML with Strict Typing
```yaml
version: "0.1"
name: "typed-workflow"
steps:
  - id: "welcome"
    uses: "debug.echo"
    message: "Hello World"
    level: "info"  # Only valid values allowed
  
  - id: "process"
    uses: "python.eval"
    expression: "len(data) * 2"
    globals:
      data: "{{ input_data }}"
  
  - id: "api-call"
    uses: "http.request"
    method: "GET"  # Only valid HTTP methods
    url: "https://api.example.com"
    timeout: 30
```

### Type-Safe Access in Code
```python
for step in workflow.steps:
    if isinstance(step, DebugEchoStep):
        # IDE knows step has message, level, timestamp fields
        print(f"Echo: {step.message} at level {step.level}")
    
    elif isinstance(step, PythonEvalStep):
        # IDE knows step has expression, globals, locals fields
        print(f"Evaluating: {step.expression}")
    
    elif isinstance(step, HttpRequestStep):
        # IDE knows step has method, url, headers, body fields
        print(f"HTTP {step.method} to {step.url}")
```

## Conclusion

The strictly typed approach provides:
- **Better Developer Experience**: IDE support, autocomplete, compile-time validation
- **Better User Experience**: Clear error messages, documentation in code
- **Better Maintainability**: Easy to add tools, type-safe access
- **Better Reliability**: Runtime validation, no more generic dict access

This approach transforms Petal from a generic workflow system to a type-safe, developer-friendly platform with excellent tooling support.
