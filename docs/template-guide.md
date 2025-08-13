# Documentation Template Guide

This guide explains how to use and customize the documentation template for your project.

## Overview

The documentation is built using **Sphinx** with **MyST** (Markdown) support, providing a modern, maintainable documentation system.

## Structure

```
docs/
├── source/                    # Sphinx source files
│   ├── conf.py               # Sphinx configuration (templated)
│   ├── index.md              # Main documentation page (templated)
│   ├── api.md                # API documentation template
│   ├── contributing.md       # Contributing guidelines (templated)
│   ├── dependency-groups.md  # Dependency explanation (templated)
│   ├── _static/              # Static assets (CSS, images)
│   └── _templates/           # Sphinx templates
├── adr/                      # Architecture Decision Records
│   └── 0001-template-design.md
├── Makefile                  # Build commands
└── template-guide.md         # This file
```

## Customization

### 1. Update Project Information

The following files are templated with your project information:

- `docs/source/conf.py` - Project name, author, version
- `docs/source/index.md` - Project description
- `docs/source/contributing.md` - GitHub repository URLs
- `docs/source/dependency-groups.md` - Project name

### 2. Customize API Documentation

Edit `docs/source/api.md` to include your project's modules:

```markdown
### your_project.core

```{automodule} your_project.core
:members:
:undoc-members:
:show-inheritance:
```
```

### 3. Add Custom Content

- **New pages**: Add `.md` files to `docs/source/` and include them in the toctree
- **Static assets**: Place images, CSS, etc. in `docs/source/_static/`
- **Custom templates**: Add Jinja2 templates to `docs/source/_templates/`

### 4. Architecture Decisions

Add new ADRs to `docs/adr/` following the format:

```markdown
# ADR 0002: Your Decision

## Status

Proposed

## Context

Brief description of the problem or situation.

## Decision

What was decided and why.

## Consequences

Positive and negative consequences.
```

## Building Documentation

### Local Development

```bash
# Install documentation dependencies
uv pip install -e ".[docs]"

# Build documentation
cd docs && make html

# View locally
open _build/html/index.html
```

### Using Nox

```bash
# Build documentation
nox -s docs

# Check links
nox -s docs_linkcheck
```

### Using Just

```bash
# Build documentation
just docs
```

## Configuration

### Sphinx Extensions

The template includes these Sphinx extensions:

- `sphinx.ext.autodoc` - Auto-generate API docs from docstrings
- `sphinx.ext.napoleon` - Google/NumPy docstring support
- `sphinx.ext.viewcode` - Link to source code
- `sphinx.ext.githubpages` - GitHub Pages integration
- `myst_parser` - Markdown support

### Theme

Uses **Furo** theme for modern, clean appearance.

### MyST Extensions

Enabled MyST extensions for enhanced Markdown:

- `colon_fence` - Code blocks with colons
- `deflist` - Definition lists
- `dollarmath` - LaTeX math
- `fieldlist` - Field lists
- `html_admonition` - HTML admonitions
- `html_image` - HTML images
- `replacements` - Text replacements
- `smartquotes` - Smart quotes
- `strikethrough` - Strikethrough text
- `substitution` - Variable substitution
- `tasklist` - Task lists

## Best Practices

1. **Use docstrings**: All public APIs should have comprehensive docstrings
2. **Include examples**: Add usage examples in docstrings and documentation
3. **Keep it current**: Update documentation when APIs change
4. **Test links**: Use `nox -s docs_linkcheck` to verify all links work
5. **Version control**: Include documentation changes in the same PR as code changes

## CI/CD Integration

The template includes GitHub Actions workflows that:

- Build documentation on every PR
- Deploy to GitHub Pages on main branch
- Check for broken links
- Validate documentation structure

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure your package is installed in editable mode
2. **Missing modules**: Update `docs/source/api.md` to include new modules
3. **Build failures**: Check that all dependencies are installed with `uv pip install -e ".[docs]"`

### Getting Help

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Documentation](https://myst-parser.readthedocs.io/)
- [Furo Theme](https://pradyunsg.me/furo/)
