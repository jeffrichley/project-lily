# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **New CLI Commands**: Added `lily compose` and `lily info` commands for workflow management
- **Comprehensive Examples**: Added new petal workflow examples including data processing, web scraping, and file backup
- **Integration Tests**: Added comprehensive CLI integration tests with real command execution
- **Migration Documentation**: Added detailed migration plan and documentation for Hydra removal
- **Archon Integration**: Added Archon workflow management and task tracking system

### Changed
- **Major Architecture Overhaul**: Completely removed Hydra integration and simplified the architecture
- **CLI Simplification**: Replaced complex Hydra subcommands with simple, direct CLI commands
- **Composition Engine**: Rewrote composition engine to work with direct file paths instead of Hydra configs
- **Parser System**: Simplified parser to use basic YAML parsing without Hydra dependencies
- **Documentation**: Updated all documentation to reflect simplified architecture and remove Hydra references

### Removed
- **Hydra Dependencies**: Removed `hydra-core` and `omegaconf` dependencies completely
- **Hydra Integration Files**: Deleted all Hydra-specific integration files and demo scripts
- **Complex Configuration**: Removed complex Hydra configuration hierarchies and multirun support
- **Hydra Tests**: Removed all Hydra-specific test files and test cases
- **Hydra Examples**: Removed all Hydra-based example configurations

### Fixed
- **Test Coverage**: Fixed test mocking strategies to focus on actual functionality
- **Error Handling**: Improved error handling to be more generic and helpful
- **Documentation**: Fixed outdated documentation references and examples
- **Dependency Management**: Cleaned up project dependencies and removed unused packages

## [0.1.0] - 2025-08-14

### Added
- **Initial Release**: First public release of Lily project
- **Core Petal DSL**: Basic petal file parsing, validation, and templating
- **CLI Framework**: Basic CLI structure with Typer integration
- **Testing Framework**: Comprehensive test suite with pytest
- **Documentation**: Initial documentation and examples
- **Quality Gates**: Linting, type checking, and coverage requirements

### Technical Details
- **Language**: Python 3.12+
- **CLI Framework**: Typer
- **Testing**: pytest with comprehensive coverage
- **Linting**: Ruff with strict rules
- **Type Checking**: MyPy with strict mode
- **Documentation**: Sphinx with modern theme
- **Dependency Management**: uv with lock files

---

## Migration Notes

### From Hydra-based to Native Architecture
This release represents a major architectural change from Hydra-based configuration management to a native, simplified architecture:

#### What Changed
- **CLI Commands**: `hydra_compose` → `lily compose <file>`
- **Configuration**: Complex Hydra configs → Simple petal files
- **Dependencies**: Removed `hydra-core` and `omegaconf`
- **Architecture**: Hydra integration → Native composition engine

#### What Stayed the Same
- **Petal File Format**: No breaking changes to .petal file syntax
- **Core Functionality**: All core petal features preserved
- **API Compatibility**: Internal APIs remain compatible
- **Examples**: Updated to work with new architecture

#### Migration Path
1. **Immediate**: Update CLI commands to use new syntax
2. **Optional**: Remove any Hydra-specific configuration files
3. **Future**: No additional migration steps required

### Breaking Changes
- **CLI Commands**: Changed from Hydra subcommands to direct commands
- **Configuration**: Removed support for Hydra configuration hierarchies
- **Dependencies**: Removed Hydra-related packages

### Deprecations
- **Hydra Integration**: All Hydra integration features have been removed
- **Complex Configuration**: Multirun and complex override systems removed
- **Hydra-specific APIs**: All Hydra-specific APIs have been removed
