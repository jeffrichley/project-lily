# Core CLI Framework Specification

**Status**: In Progress
**Created**: 2025-08-12
**Author**: Jeff Richley
**Priority**: High
**Estimated Effort**: 2 weeks

## Problem Statement

Project Lily needs a solid foundation for command-line interaction. The core CLI framework must provide the basic infrastructure for the interactive shell, command parsing, and configuration management that will support all other features.

## Goals and Success Criteria

### Goals
- ✅ Provide a robust CLI entry point with `lily` command
- ✅ Implement configuration management system
- ✅ Create basic interactive shell framework
- ✅ Establish proper error handling and logging
- ✅ Set up project structure for future development

### Success Criteria
- ✅ Users can run `lily` command successfully
- ✅ Configuration is loaded from `~/.lily/config.toml`
- ✅ Interactive shell starts and responds to basic input
- ✅ Proper error messages are displayed for common issues
- ✅ Project structure supports modular development

## Technical Design

### Overview
The core CLI framework has been built using Typer for command-line argument parsing, Rich for terminal output, and a modular architecture that separates concerns between CLI, configuration, and shell components.

The look and feel theme is documented in ./docs/planning/lily_cli_theme.md and has been implemented with a beautiful purple "iris-bloom" theme.

### Implementation Status
- ✅ **CLI Framework**: Complete with Typer-based command structure
- ✅ **Configuration System**: Complete with Pydantic models and TOML persistence
- ✅ **Theme System**: Complete with Rich themes and theme switching
- ✅ **Interactive Shell**: Complete with prompt-toolkit integration
- ✅ **Error Handling**: Complete with Rich-styled error messages
- ✅ **Project Structure**: Complete with modular architecture

### Data Models

#### Configuration Model ✅ IMPLEMENTED
```python
class LilyConfig(BaseModel):
    openai_api_key: str
    model: str = "gpt-4"
    max_tokens: int = 4000
    temperature: float = 0.7
    commands_dir: Path = Path("~/.lily/commands")
    rules_dir: Path = Path("~/.lily/rules")
    sessions_dir: Path = Path("~/.lily/sessions")
    theme: ThemeName = ThemeName.IRIS_BLOOM
    history_size: int = 1000
    auto_complete: bool = True
```

#### Shell State Model ✅ IMPLEMENTED
```python
@dataclass
class ShellState:
    config: LilyConfig
    session_id: str
    conversation_history: list[Message]
    available_commands: list[Command]
    is_running: bool = True
```

### APIs

#### CLI Entry Point ✅ IMPLEMENTED
```python
import typer

app = typer.Typer(
    name="lily",
    help="🌙 Lily - Software development project planning and organization tool",
    add_completion=False,
    rich_markup_mode="rich",
)

@app.command()
def start(config: Path | None = typer.Option(None, help='Path to config file')):
    """Start the Lily interactive shell"""
    # Implementation complete

@app.command()
def run(file: Path = typer.Argument(..., help='Path to .petal file')):
    """Run a .petal file directly"""
    # Implementation complete

@app.command()
def config(show: bool = typer.Option(False, help='Show current config')):
    """Manage Lily configuration"""
    # Implementation complete

@app.command()
def version():
    """Show Lily version"""
    # Implementation complete
```

#### Configuration Manager ✅ IMPLEMENTED
```python
class ConfigManager:
    def load_config(self, config_path: Path | None = None) -> LilyConfig
    def save_config(self, config: LilyConfig) -> None
    def validate_config(self, config: LilyConfig) -> bool
    def create_default_config(self) -> LilyConfig
    def show_config(self, config: LilyConfig) -> None
    def update_config(self, **kwargs) -> None
```

#### Shell Manager ✅ IMPLEMENTED
```python
class ShellManager:
    def start_shell(self, config: LilyConfig) -> None
    def process_input(self, input_text: str) -> str
    def handle_command(self, command: str) -> str
    def exit_shell(self) -> None
    def register_command(self, command: Command) -> None
```

### Security Considerations
- Validate all configuration values
- Sanitize user inputs
- Use environment variables for sensitive data
- Implement proper error handling without information leakage

## Implementation Plan

### Phase 1: Project Structure and Dependencies
- [x] Set up project structure with src/lily/
- [x] Add required dependencies to pyproject.toml
- [x] Create basic package structure
- [x] Set up entry points

### Phase 2: Configuration System
- [x] Implement ConfigManager class
- [x] Create configuration validation
- [x] Add environment variable support
- [x] Implement default configuration generation

### Phase 3: CLI Framework
- [x] Implement main CLI entry point
- [x] Add command-line argument parsing
- [x] Create basic command structure
- [x] Implement help and version commands

### Phase 4: Basic Shell
- [x] Create ShellManager class
- [x] Implement basic input/output loop
- [x] Add graceful exit handling
- [x] Create session management foundation

## Testing Strategy

### Unit Tests
- Test configuration loading and validation
- Test CLI argument parsing
- Test shell state management
- Test error handling scenarios

### Integration Tests
- Test full CLI workflow
- Test configuration file creation
- Test shell startup and shutdown
- Test command-line argument handling

### End-to-End Tests
- Test `lily` command execution
- Test interactive shell basic functionality
- Test configuration file management
- Test error scenarios

## Documentation Requirements

- [x] Update README with installation and basic usage
- [x] Document configuration options
- [x] Add CLI command reference
- [ ] Create troubleshooting guide
- [x] Document project structure

## Risks and Mitigation

### Risks
- **Complexity**: Keep initial implementation simple and focused
- **Dependencies**: Use well-established, maintained libraries
- **Configuration**: Provide clear defaults and validation
- **Error Handling**: Implement comprehensive error handling from start

### Backward Compatibility
- No backward compatibility concerns for initial implementation
- Future changes will maintain compatibility with configuration format

## Review Checklist

- [x] Technical design reviewed
- [x] Security implications considered
- [x] Performance impact assessed
- [x] Testing strategy defined
- [x] Documentation plan created
- [x] Dependencies evaluated
- [x] Error handling strategy defined
