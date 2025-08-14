# Project Lily

[![CI](https://github.com/jeffrichley/lily/workflows/CI/badge.svg)](https://github.com/jeffrichley/lily/actions)
[![Codecov](https://codecov.io/gh/jeffrichley/lily/branch/main/graph/badge.svg)](https://codecov.io/gh/jeffrichley/lily)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit enabled](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Ruff](https://img.shields.io/badge/ruff-enabled-brightgreen?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![MyPy](https://img.shields.io/badge/mypy-enabled-brightgreen?logo=mypy&logoColor=white)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![pip-audit](https://img.shields.io/badge/pip--audit-enabled-brightgreen?logo=security&logoColor=white)](https://pypi.org/project/pip-audit/)
![pyproject validated](https://img.shields.io/badge/pyproject%20schema-valid-brightgreen?style=flat-square)

A modern, declarative workflow automation system with a simple CLI interface.

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jeffrichley/lily.git
cd lily

# Install with uv (recommended)
uv sync

# Or install with pip
pip install -e .
```

### Development Setup

```bash
# Install in editable mode with development dependencies
uv pip install -e ".[dev]"

# Run quality checks
uv run dev checkit

# Run tests
uv run dev test

# Build documentation
uv run dev docs
```

## 📦 Usage

### Basic Workflow Execution

```bash
# Compose and run a Petal workflow
lily compose examples/hello_world.petal

# Run with dry-run mode to see what would happen
lily compose examples/hello_world.petal --dry-run

# Get information about a workflow
lily info examples/hello_world.petal
```

### Creating Petal Workflows

Petal workflows are defined in YAML files with a simple, declarative syntax:

```yaml
name: "Hello World"
description: "A simple example workflow"

params:
  name:
    type: "str"
    default: "World"
    help: "Name to greet"

steps:
  - id: "greet"
    uses: "shell"
    command: "echo 'Hello, {{ params.name }}!'"
```

## 🧪 Testing

```bash
# Run all tests
uv run dev test

# Run with coverage
uv run dev test --cov

# Run specific test file
uv run pytest tests/unit/test_example.py
```

## 📚 Documentation

- **[API Reference](docs/api.md)**: Complete API documentation
- **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to the project
- **[Petal DSL Guide](docs/planning/petal/)**: Petal workflow language documentation

## 🛠️ Development

### Quality Checks

```bash
# Run all quality checks
uv run dev checkit

# Individual checks
uv run dev lint          # Code linting
uv run dev typecheck     # Type checking
uv run dev format        # Code formatting
```

### Project Structure

```
lily/
├── src/lily/           # Main package source code
│   ├── cli/           # Command-line interface
│   ├── petal/         # Petal DSL implementation
│   └── compose/       # Workflow composition engine
├── tests/             # Test suite
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── e2e/           # End-to-end tests
├── examples/          # Example Petal workflows
├── docs/              # Documentation
└── README.md          # This file
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Setup

```bash
# Install development dependencies
uv pip install -e ".[dev,docs]"

# Run quality checks
uv run dev checkit

# Make your changes and test
uv run dev test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎉 Acknowledgments

- Built with modern Python best practices
- Designed for maintainability and extensibility
- Simple, declarative workflow automation

---

**Project Lily** - Modern workflow automation with declarative YAML
