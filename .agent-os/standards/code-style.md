# Project Lily Code Style Standards

## Python Code Style

### General Principles
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Prefer explicit over implicit
- Write self-documenting code with clear variable names
- Keep functions small and focused on a single responsibility

### Formatting
- Use Black for code formatting (line length: 88 characters)
- Use Ruff for linting and import sorting
- Use isort for import organization
- Maximum line length: 88 characters

### Naming Conventions
- **Classes**: PascalCase (e.g., `LilyShell`, `CommandExecutor`)
- **Functions and Variables**: snake_case (e.g., `start_shell`, `config_path`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_CONFIG_PATH`)
- **Private Methods**: Leading underscore (e.g., `_load_config`)
- **Protected Methods**: Leading underscore (e.g., `_validate_input`)

### Type Hints
- Use type hints for all function signatures
- Avoid `Any` type - use specific types or `Union`/`Optional`
- Use `from typing import` for complex types
- Prefer `list[str]` over `List[str]` (Python 3.9+)

### Documentation
- Use docstrings for all public functions and classes
- Follow Google docstring format
- Include type information in docstrings
- Document exceptions that may be raised

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Use context managers for resource management
- Log errors with appropriate levels

## Project Structure

### Module Organization
```
src/lily/
├── __init__.py
├── cli.py              # CLI entry point
├── shell.py            # Interactive shell
├── config.py           # Configuration management
├── commands/           # Command system
│   ├── __init__.py
│   ├── executor.py
│   └── parser.py
├── ai/                 # AI integration
│   ├── __init__.py
│   ├── client.py
│   └── conversation.py
└── utils/              # Utility functions
    ├── __init__.py
    └── helpers.py
```

### Import Organization
1. Standard library imports
2. Third-party imports
3. Local application imports
4. Separate groups with blank lines

### File Naming
- Use lowercase with underscores for Python files
- Use descriptive names that indicate purpose
- Keep file names short but meaningful

## Testing Standards

### Test Organization
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- End-to-end tests in `tests/e2e/`
- Test files should mirror source structure

### Test Naming
- Test functions: `test_<function_name>_<scenario>`
- Test classes: `Test<ClassName>`
- Use descriptive test names that explain the scenario

### Test Structure
- Use pytest fixtures for setup and teardown
- Mock external dependencies
- Test both success and failure cases
- Use parametrized tests for multiple scenarios

### Coverage Requirements
- Minimum 90% code coverage
- 100% coverage for critical paths
- Test all public APIs
- Include edge cases and error conditions

## Configuration Standards

### Configuration Files
- Use TOML format for configuration
- Provide sensible defaults
- Validate configuration on load
- Use environment variables for secrets

### Environment Variables
- Prefix with `LILY_` (e.g., `LILY_OPENAI_API_KEY`)
- Document all environment variables
- Provide clear error messages for missing required variables

## Documentation Standards

### Code Documentation
- Document all public APIs
- Include usage examples
- Document configuration options
- Keep documentation up to date with code changes

### User Documentation
- Clear installation instructions
- Usage examples and tutorials
- Configuration reference
- Troubleshooting guide

## Security Standards

### Input Validation
- Validate all user inputs
- Sanitize file paths and commands
- Use parameterized queries for database operations
- Implement proper access controls

### Secret Management
- Never hardcode secrets
- Use environment variables for API keys
- Implement secure configuration storage
- Log security events appropriately

## Performance Standards

### Code Performance
- Profile critical code paths
- Optimize for common use cases
- Use appropriate data structures
- Minimize memory allocations

### Startup Time
- Target < 2 seconds for initial startup
- Lazy load heavy dependencies
- Cache frequently accessed data
- Optimize import times
