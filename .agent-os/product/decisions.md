# Project Lily Decision History

## Architecture Decisions

### 2025-08-12: Project Structure and Tooling
**Decision**: Use modern Python tooling stack (uv, nox, just, pytest, typer)
**Rationale**:
- uv provides faster dependency resolution than pip
- nox enables reproducible development environments
- just simplifies common development tasks
- pytest is the de facto standard for Python testing
**Alternatives Considered**: pip + make, poetry + tox, click
**Status**: Implemented

### 2025-08-12: Configuration Format
**Decision**: Use TOML for configuration files
**Rationale**:
- Human-readable and writable
- Supports nested structures
- Widely adopted in Python ecosystem
- Better than JSON for configuration
**Alternatives Considered**: YAML, JSON, INI
**Status**: Planned

### 2025-08-12: Command File Format
**Decision**: Use `.petal` extension for custom command files
**Rationale**:
- Distinctive and memorable
- Avoids conflicts with existing file types
- Supports markdown content with custom metadata
- Enables both LLM and script execution
**Alternatives Considered**: `.lily`, `.cmd`, `.md`
**Status**: Planned

### 2025-08-12: AI Provider
**Decision**: Start with OpenAI API as primary LLM provider
**Rationale**:
- Most mature and reliable API
- Excellent documentation and support
- Wide adoption and community knowledge
- Can be extended to support other providers later
**Alternatives Considered**: Anthropic Claude, Google Gemini, Local models
**Status**: Planned

### 2025-08-12: Terminal UI Framework
**Decision**: Use Rich + Prompt Toolkit for terminal interface
**Rationale**:
- Rich provides excellent colored output and formatting
- Prompt Toolkit offers advanced REPL features
- Both are well-maintained and widely used
- Good integration with Python ecosystem
**Alternatives Considered**: Textual, blessed, urwid
**Status**: Planned

### 2025-08-12: Session Storage
**Decision**: Use JSON for session persistence
**Rationale**:
- Simple and human-readable
- Good Python support
- Easy to debug and inspect
- Sufficient for session data complexity
**Alternatives Considered**: SQLite, YAML, pickle
**Status**: Planned

### 2025-08-12: Configuration Location
**Decision**: Use `~/.lily/` for global configuration
**Rationale**:
- Follows Unix/Linux conventions
- Clear separation from application code
- Easy to backup and version control
- Accessible across different installations
**Alternatives Considered**: `/etc/lily/`, `./.lily/`, `$XDG_CONFIG_HOME/lily/`
**Status**: Planned

## Implementation Decisions

### 2025-08-12: Project Naming
**Decision**: Name the project "Lily"
**Rationale**:
- Short, memorable, and unique
- Evokes growth and development (like a flower)
- Available as package name on PyPI
- Works well for command-line usage
**Alternatives Considered**: Agent, Shell, Assistant, Terminal
**Status**: Implemented

### 2025-08-12: Command Discovery
**Decision**: Auto-discover commands from `~/.lily/commands/` directory
**Rationale**:
- Simple and intuitive for users
- No manual registration required
- Easy to add/remove commands
- Follows filesystem conventions
**Alternatives Considered**: Registry system, configuration-based discovery
**Status**: Planned

### 2025-08-12: Slash Command Prefix
**Decision**: Use `/` as prefix for custom commands
**Rationale**:
- Familiar from chat applications
- Clear distinction from regular conversation
- Easy to type and remember
- Supports tab completion naturally
**Alternatives Considered**: `!`, `>`, `:`
**Status**: Planned

## Future Considerations

### Multi-Provider AI Support
**Consideration**: Support multiple LLM providers
**Timeline**: Post-MVP
**Impact**: Increases complexity but improves flexibility

### Plugin System
**Consideration**: Allow third-party plugins
**Timeline**: Future enhancement
**Impact**: Enables ecosystem growth but requires careful API design

### Cloud Sync
**Consideration**: Sync configurations across devices
**Timeline**: Future enhancement
**Impact**: Improves user experience but adds complexity and privacy concerns
