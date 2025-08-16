"""Nox automation file for Project Lily.

Key features:
- Uses `uv` for dependency installation.
- Supports Python 3.13 (matrix-ready).
- Sessions: tests, lint, type_check, docs, precommit, coverage_html, complexity, security, pyproject.
- Re-uses local virtualenvs for speed; CI passes `--force-python` to isolate.
- Parametrized "mode" for minimal vs full extras install.

Generated from the Seedling Copier template.
"""

from pathlib import Path

import nox

# -------- Global config -------- #
nox.options.sessions = [
    "tests",
    "lint",
    "type_check",
    "docs",
    "complexity",
    "security",
    "pyproject",
]
# Re‑use existing venvs locally for speed; CI can override with --no-reuse-existing-virtualenvs
nox.options.reuse_existing_virtualenvs = True

PROJECT_ROOT = Path(__file__).parent

PYTHON_VERSIONS = ["3.13"]  # Using Python 3.13 for PEP 695 support
INSTALL_MODES = ["minimal", "full"]  # "minimal" == core deps only; "full" == dev[all]


def install_project(session: nox.Session, mode: str = "minimal") -> None:
    """Install the project with uv and the chosen extras mode."""
    assert mode in INSTALL_MODES
    extras = "" if mode == "minimal" else "[dev]"
    session.run("uv", "pip", "install", "-q", "-e", f".{extras}", external=True)
    # Always install core test dependencies
    session.run(
        "uv",
        "pip",
        "install",
        "-q",
        "pytest",
        "pytest-cov",
        "pytest-asyncio",
        "hypothesis",
        external=True,
    )


# -------- Sessions -------- #


@nox.session(python=PYTHON_VERSIONS)
@nox.parametrize("mode", INSTALL_MODES)
def tests(session: nox.Session, mode: str) -> None:
    """Run pytest with coverage."""
    install_project(session, mode)
    session.run(
        "pytest",
        "tests",
        "--disable-warnings",
        "--cov=src",
        "--cov-report=term-missing",
        external=True,
    )


@nox.session(python=PYTHON_VERSIONS[0])
def lint(session: nox.Session) -> None:
    """Run Ruff autofix + Black formatting."""
    session.run("uv", "pip", "install", "-q", "ruff", "black", external=True)
    session.run("ruff", "check", "src", "tests", "--fix")
    session.run("black", "src", "tests")


@nox.session(python=PYTHON_VERSIONS[0])
def type_check(session: nox.Session) -> None:
    """Run MyPy type checks."""
    install_project(session, "full")
    session.run("mypy", "src", "tests")


@nox.session(python=PYTHON_VERSIONS[0])
def docs(session: nox.Session) -> None:
    """Build Sphinx docs."""
    install_project(session, "full")
    session.run("uv", "pip", "install", "-q", "-e", ".[docs]", external=True)
    session.run("sphinx-build", "-W", "docs/source", "docs/build")


@nox.session(python=PYTHON_VERSIONS[0])
def docs_linkcheck(session: nox.Session) -> None:
    """Check Sphinx docs links."""
    install_project(session, "full")
    session.run("uv", "pip", "install", "-q", "-e", ".[docs]", external=True)
    session.run(
        "sphinx-build", "-b", "linkcheck", "docs/source", "docs/build/linkcheck"
    )


@nox.session(python=PYTHON_VERSIONS[0], name="pre-commit")
def precommit_hooks(session: nox.Session) -> None:
    """Run pre-commit hooks on all files."""
    session.run("uv", "pip", "install", "-q", "pre-commit", external=True)
    session.run("pre-commit", "run", "--all-files")


@nox.session(python=PYTHON_VERSIONS[0])
def coverage_html(session: nox.Session) -> None:
    """Generate an HTML coverage report."""
    session.run("uv", "pip", "install", "-q", "coverage[toml]", external=True)
    session.run("coverage", "html")
    html_path = PROJECT_ROOT / "htmlcov" / "index.html"
    session.log(f"Generated coverage HTML at {html_path.as_uri()}")


# ---------------- Extra quality sessions ---------------- #


@nox.session(python=PYTHON_VERSIONS[0])
def complexity(session: nox.Session) -> None:
    """Fail if cyclomatic complexity exceeds score B."""
    session.run("uv", "pip", "install", "-q", "xenon", external=True)
    # Tweak --max-absolute (A=0, B=10, C=20) to your tolerance
    session.run("xenon", "--max-absolute", "B", "src")


@nox.session(python=PYTHON_VERSIONS[0])
def security(session: nox.Session) -> None:
    """Run pip-audit against project dependencies."""
    session.run("uv", "pip", "install", "-q", "pip-audit", external=True)
    # Audit direct + transitive deps pinned in uv.lock
    session.run("pip-audit", "--progress-spinner=off")


@nox.session(python=PYTHON_VERSIONS[0])
def pyproject(session: nox.Session) -> None:
    """Validate pyproject.toml configuration."""
    session.run("uv", "pip", "install", "-q", "-e", ".", external=True)
    session.run("uv", "pip", "install", "-q", "validate-pyproject", external=True)
    session.run("validate-pyproject", "pyproject.toml")
