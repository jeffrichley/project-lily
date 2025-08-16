# 🌙 Lily

Software development project planning and organization tool.

## Features

- **Modern Python Tooling**: Built with uv, nox, and just for optimal development experience
- **Quality Assurance**: Comprehensive testing, linting, and type checking
- **Documentation**: Automated documentation generation with Sphinx
- **CI/CD Ready**: Pre-configured GitHub Actions workflows
- **Type Safety**: Full type hints and mypy integration
- **Extensible Architecture**: Modular design with plugin support

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/lily.git
cd lily

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

### Development

```bash
# Run tests
just test

# Run linting
just lint

# Run type checking
just type-check

# Build documentation
just docs

# Run all quality checks
just quality
```

### Usage

```bash
# Start the interactive shell
lily start

# Show version
lily version

# Manage configuration
lily config
```

## Project Structure

```
lily/
├── src/lily/           # Main package
│   ├── cli/           # Command-line interface
│   ├── config.py      # Configuration management
│   ├── shell.py       # Shell command execution
│   ├── theme.py       # Theme management
│   └── types.py       # Type definitions
├── tests/             # Test suite
├── docs/              # Documentation
├── examples/          # Example usage
└── pyproject.toml     # Project configuration
```

## Development

### Prerequisites

- Python 3.8+
- uv (recommended) or pip
- just (optional, for development shortcuts)

### Setup

1. **Install uv** (recommended package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install just** (optional, for development shortcuts):
   ```bash
   # macOS
   brew install just
   
   # Linux
   cargo install just
   ```

3. **Clone and setup**:
   ```bash
   git clone https://github.com/your-org/lily.git
   cd lily
   uv sync
   ```

### Development Commands

```bash
# Run tests
just test

# Run all tests (unit, integration, e2e)
just test-all

# Run linting
just lint

# Run type checking
just type-check

# Build documentation
just docs

# Run all quality checks
just quality

# Install development dependencies
just install

# Clean up generated files
just clean
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for all public functions
- Keep functions small and focused

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting
- Aim for high test coverage

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/your-org/lily/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/lily/discussions)
- **Documentation**: [docs/](docs/)

## Roadmap

- [ ] Enhanced CLI features
- [ ] Plugin system
- [ ] Integration with popular development tools
- [ ] Cloud deployment support
- [ ] Team collaboration features
