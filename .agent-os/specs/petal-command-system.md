# Petal Command System Specification

**Status**: Ready for Implementation 🚀
**Created**: 2025-08-12
**Author**: Jeff Richley
**Priority**: High
**Estimated Effort**: 3 weeks

## Problem Statement

Project Lily needs a flexible and extensible command system that allows users to create custom commands using `.petal` files. These files should support both LLM-based execution and traditional script execution, with a clear format that's easy to write and understand.

## Goals and Success Criteria

### Goals
- Create `.petal` file format for custom commands
- Implement command discovery and registration system
- Support both LLM and script execution modes
- Provide tab completion for slash commands
- Enable command chaining and parameter passing

### Success Criteria
- Users can create `.petal` files in `~/.lily/commands/`
- Commands are automatically discovered and available as slash commands
- Tab completion works for all available commands
- Both LLM and script execution modes work correctly
- Commands can accept parameters and arguments

## Technical Design

### Overview
The petal command system will use markdown files with YAML frontmatter for metadata, supporting both LLM-based execution (using natural language instructions) and traditional script execution (using code blocks).

### Data Models

#### Petal Command Model
```python
@dataclass
class PetalCommand:
    name: str
    description: str
    file_path: Path
    execution_mode: ExecutionMode
    parameters: list[Parameter]
    content: str
    metadata: dict[str, Any]

@dataclass
class Parameter:
    name: str
    type: str
    description: str
    required: bool = False
    default: Any = None

class ExecutionMode(Enum):
    LLM = "llm"
    SCRIPT = "script"
    HYBRID = "hybrid"
```

#### Command Registry Model
```python
@dataclass
class CommandRegistry:
    commands: dict[str, PetalCommand]
    categories: dict[str, list[str]]
    
    def register_command(self, command: PetalCommand) -> None
    def get_command(self, name: str) -> PetalCommand | None
    def list_commands(self) -> list[str]
    def get_commands_by_category(self, category: str) -> list[PetalCommand]
```

### APIs

#### Command Parser
```python
class PetalParser:
    def parse_file(self, file_path: Path) -> PetalCommand
    def parse_content(self, content: str) -> PetalCommand
    def validate_command(self, command: PetalCommand) -> bool
    def extract_metadata(self, content: str) -> dict[str, Any]
```

#### Command Executor
```python
class CommandExecutor:
    def execute_llm_command(self, command: PetalCommand, args: dict[str, Any]) -> str
    def execute_script_command(self, command: PetalCommand, args: dict[str, Any]) -> str
    def execute_hybrid_command(self, command: PetalCommand, args: dict[str, Any]) -> str
    def validate_args(self, command: PetalCommand, args: dict[str, Any]) -> bool
```

#### Command Discovery
```python
class CommandDiscovery:
    def discover_commands(self, commands_dir: Path) -> list[PetalCommand]
    def watch_directory(self, commands_dir: Path) -> None
    def reload_commands(self) -> None
    def get_command_suggestions(self, partial: str) -> list[str]
```

### File Format

#### LLM Command Example
```markdown
---
name: analyze_code
description: Analyze code for potential improvements
mode: llm
parameters:
  - name: file
    type: path
    description: Path to the file to analyze
    required: true
  - name: focus
    type: string
    description: What to focus on (performance, security, style)
    default: "all"
category: code_analysis
---

This command analyzes the specified code file for potential improvements.

## Instructions

1. Read the specified file
2. Analyze the code for the requested focus areas
3. Provide specific, actionable recommendations
4. Include code examples where appropriate
5. Prioritize recommendations by impact

## Context

The user wants to improve their code quality and maintainability.
```

#### Script Command Example
```markdown
---
name: git_status
description: Show git status with custom formatting
mode: script
parameters:
  - name: format
    type: string
    description: Output format (short, long, json)
    default: "short"
category: git
---

```python
import subprocess
import json
import sys

def main():
    format_type = args.get('format', 'short')
    
    if format_type == 'json':
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        # Parse and format as JSON
        status_lines = result.stdout.strip().split('\n')
        status_data = []
        for line in status_lines:
            if line:
                status, file_path = line[:2], line[3:]
                status_data.append({
                    'status': status,
                    'file': file_path
                })
        print(json.dumps(status_data, indent=2))
    else:
        subprocess.run(['git', 'status'])
```

### Security Considerations
- Validate all file paths and prevent directory traversal
- Sandbox script execution environment
- Limit script execution permissions
- Validate command parameters before execution
- Implement command execution timeouts

## Implementation Plan

### Phase 1: File Format and Parser 🎯 NEXT PRIORITY
- [ ] Define `.petal` file format specification
- [ ] Implement PetalParser class
- [ ] Add metadata extraction and validation
- [ ] Create parameter parsing and validation

### Phase 2: Command Discovery
- [ ] Implement CommandDiscovery class
- [ ] Add directory watching for new commands
- [ ] Create command registry system
- [ ] Implement command reloading

### Phase 3: Command Execution
- [ ] Implement CommandExecutor class
- [ ] Add LLM execution mode
- [ ] Add script execution mode
- [ ] Implement hybrid execution mode

### Phase 4: Shell Integration
- [ ] Integrate with interactive shell
- [ ] Add tab completion for commands
- [ ] Implement slash command parsing
- [ ] Add command help and documentation

## Testing Strategy

### Unit Tests
- Test petal file parsing
- Test command validation
- Test parameter parsing
- Test execution modes

### Integration Tests
- Test command discovery workflow
- Test command execution end-to-end
- Test shell integration
- Test error handling

### End-to-End Tests
- Test complete command workflow
- Test file watching and reloading
- Test tab completion
- Test command chaining

## Documentation Requirements

- [ ] Document `.petal` file format
- [ ] Create command writing guide
- [ ] Add examples for different execution modes
- [ ] Document parameter types and validation
- [ ] Create troubleshooting guide

## Risks and Mitigation

### Risks
- **Security**: Implement comprehensive sandboxing and validation
- **Performance**: Cache parsed commands and optimize discovery
- **Complexity**: Keep file format simple and well-documented
- **Compatibility**: Version the file format for future changes

### Backward Compatibility
- Version the `.petal` file format
- Provide migration tools for format changes
- Maintain compatibility with existing commands

## Review Checklist

- [ ] Technical design reviewed
- [ ] Security implications considered
- [ ] Performance impact assessed
- [ ] Testing strategy defined
- [ ] Documentation plan created
- [ ] File format specification complete
- [ ] Execution modes defined
- [ ] Error handling strategy defined
