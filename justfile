# Development shortcuts for Project Lily
# Generated from the Seedling Copier template

# Run tests (default: unit tests only)
test:
    uv run pytest tests/unit/ --cov=src/lily --cov-report=term-missing

# Run all tests
test-all:
    nox -s tests

# Run specific test types
test-unit:
    uv run pytest tests/unit/ --cov=src/lily --cov-report=term-missing

test-integration:
    uv run pytest tests/integration/ --cov=src/lily --cov-report=term-missing

test-e2e:
    uv run pytest tests/e2e/ --cov=src/lily --cov-report=term-missing

# Run linting
lint:
    nox -s lint

# Run type checking
type-check:
    nox -s type_check

# Build documentation
docs:
    nox -s docs

# Check documentation links
docs-linkcheck:
    nox -s docs_linkcheck

# Run all quality checks
quality: lint type-check docs-linkcheck

# Generate coverage report
coverage:
    nox -s coverage_html

# Run security audit
security:
    nox -s security

# Run complexity analysis
complexity:
    nox -s complexity

# Validate pyproject.toml
pyproject:
    nox -s pyproject

# Run pre-commit hooks
pre-commit:
    nox -s pre-commit

# Create a release PR
release:
    gh pr create --fill --title "chore: release"

# Install development dependencies
install:
    uv sync --all-extras

# Clean up generated files
clean:
    rm -rf .nox
    rm -rf htmlcov
    rm -rf docs/build
    rm -rf .pytest_cache
    rm -rf .mypy_cache
    rm -rf .ruff_cache

# Show help
default:
    @just --list
