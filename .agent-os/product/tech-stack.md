# Project Lily Technical Architecture

## Technology Stack

### Core Framework
- **Python 3.12+**: Primary language for the application
- **Dataclasses**: Data validation and settings management
- **Rich**: Terminal UI and colored output
- **Typer**: CLI framework for command-line interface
- **Prompt Toolkit**: Interactive command-line interface with autocomplete

### AI Integration
- **OpenAI API**: Primary LLM provider for conversation and task execution
- **LangChain**: Framework for LLM orchestration and prompt management
- **Tiktoken**: Token counting and management

### Configuration & Storage
- **TOML**: Configuration file format
- **JSON**: Session storage and state management
- **Markdown**: `.petal` file format for custom commands

### Development Tools
- **uv**: Fast Python package manager
- **nox**: Task automation
- **just**: Command runner
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **mypy**: Type checking

## Architecture Overview

### Core Components

1. **Lily Shell**
   - Interactive REPL with AI conversation
   - Command history and context retention
   - Tab completion for slash commands
   - Session management

2. **Command Engine**
   - `.petal` file parser and executor
   - LLM integration for task execution
   - Script execution environment
   - Command discovery and registration

3. **Configuration Manager**
   - Global config at `~/.lily/`
   - Command directory management
   - Settings validation and defaults

4. **Session Manager**
   - Conversation history persistence
   - Context management
   - State restoration

### File Structure
```
~/.lily/
├── config.toml          # Global configuration
├── rules/              # Global rules (markdown files)
├── commands/           # Custom .petal command files
└── sessions/           # Session history and state
```

### Data Flow
1. User starts `lily` command
2. System checks `~/.lily` configuration
3. Loads global rules and available commands
4. Starts interactive shell with AI conversation
5. Processes user input (conversation or slash commands)
6. Executes commands via LLM or scripts
7. Maintains session state and history

## Security Considerations
- API key management via environment variables
- Sandboxed script execution
- Input validation and sanitization
- Secure configuration storage

## Performance Requirements
- Fast startup time (< 2 seconds)
- Responsive command execution
- Efficient memory usage for long sessions
- Minimal latency for AI interactions
