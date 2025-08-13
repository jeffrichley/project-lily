"""Sphinx configuration for Project Lily documentation.

This file contains the configuration settings for building the Sphinx documentation
for the Project Lily project.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

# -- Project information -----------------------------------------------------

project = "Project Lily"
copyright = "2025, Jeff Richley"
author = "Jeff Richley"

# Dynamic version detection
try:
    import importlib.metadata

    release = importlib.metadata.version("lily")
except importlib.metadata.PackageNotFoundError:
    release = "0.1.0"

version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "myst_parser",  # Add MyST parser for Markdown support
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: list[str] = []

# Source file suffixes
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "furo"  # Changed from sphinx_rtd_theme to furo

# Furo theme options
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#7C3AED",
        "color-brand-content": "#7C3AED",
    },
    "dark_css_variables": {
        "color-brand-primary": "#A78BFA",
        "color-brand-content": "#A78BFA",
    },
    "navigation_with_keys": True,
    "announcement": "<em>🌱 Generated with <a href='https://github.com/jeffrichley/seedling-template'>Seedling</a></em>",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Custom CSS file
html_css_files = ["custom.css"]

# -- Extension configuration -------------------------------------------------

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
}

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
