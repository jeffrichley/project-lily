# Hydra Removal Plan: Chop All Heads

## Overview
This document outlines a comprehensive plan to completely remove Hydra integration from the Lily codebase. Hydra has been identified as over-engineering that adds complexity without clear benefits, and is causing test failures and maintenance overhead.

## Phase 1: Identify and Document Hydra Dependencies

### 1.1 Files to Delete Completely
- [ ] `src/lily/cli/hydra_integration.py` - Main Hydra integration file
- [ ] `tests/unit/test_cli_hydra_integration.py` - Original Hydra tests
- [ ] `tests/unit/test_cli_hydra_integration_comprehensive.py` - Comprehensive Hydra tests
- [ ] `examples/parser_hydra_integration_demo.py` - Hydra demo file
- [ ] `conf/` directory - Entire Hydra configuration directory
  - [ ] `conf/config.yaml`
  - [ ] `conf/video_processing.yaml`
  - [ ] `conf/workflows/`
  - [ ] `conf/profiles/`
  - [ ] `conf/db/`

### 1.2 Files to Clean Up
- [ ] `pyproject.toml` - Remove Hydra dependencies
- [ ] `requirements.txt` - Remove Hydra dependencies
- [ ] Any import statements referencing Hydra in other files

### 1.3 Dependencies to Remove
- [x] `hydra-core` ✅ **REMOVED**
- [x] `omegaconf` ✅ **REMOVED** (was only used by Hydra)
- [x] Any other Hydra-related packages ✅ **REMOVED**

## Phase 2: Remove Hydra from Core Code

### 2.1 Clean Up CLI Main
**File**: `src/lily/cli/main.py`
- [ ] Remove any Hydra-related imports
- [ ] Remove any Hydra-related error handling
- [ ] Ensure Typer CLI is the only CLI framework

### 2.2 Clean Up Command Files
**Files**: `src/lily/cli/commands/*.py`
- [ ] Remove any Hydra imports or references
- [ ] Simplify error handling (remove Hydra-specific error messages)
- [ ] Ensure all commands work with simple Typer interface

### 2.3 Clean Up Composition Engine
**File**: `src/lily/compose/engine.py`
- [ ] Remove any Hydra-specific composition logic
- [ ] Ensure engine works with simple petal file paths
- [ ] Remove any Hydra configuration dependencies

### 2.4 Clean Up Parser
**File**: `src/lily/petal/parser.py`
- [ ] Remove any Hydra ConfigStore integration
- [ ] Ensure parser works with simple YAML parsing
- [ ] Remove any Hydra-specific validation

## Phase 3: Simplify CLI Commands

### 3.1 Replace Hydra Integration with Simple Commands
**Current Hydra commands to replace**:
- `hydra_compose` → `lily compose <file>`
- `hydra_info` → `lily info [file]`

**New simple command structure**:
```python
@app.command()
def compose(file: Path = typer.Argument(..., help="Petal file to compose")):
    """Compose a petal workflow."""
    pass

@app.command()
def info(file: Path = typer.Option(None, help="Petal file to inspect")):
    """Show information about petal workflows."""
    pass
```

### 3.2 Update Main CLI
**File**: `src/lily/cli/main.py`
- [ ] Add compose and info commands to main CLI
- [ ] Remove any references to Hydra CLI
- [ ] Ensure all commands use consistent error handling

## Phase 4: Rewrite Tests

### 4.1 Delete All Hydra Tests
- [ ] Delete `tests/unit/test_cli_hydra_integration.py`
- [ ] Delete `tests/unit/test_cli_hydra_integration_comprehensive.py`
- [ ] Remove any Hydra-related test fixtures

### 4.2 Write Simple Integration Tests
**New test file**: `tests/integration/test_cli_commands.py`
```python
def test_compose_command_success():
    """Test compose command with valid petal file."""
    # Simple test without complex mocking
    
def test_info_command_success():
    """Test info command with valid petal file."""
    # Simple test without complex mocking
    
def test_compose_command_invalid_file():
    """Test compose command with invalid file."""
    # Simple error handling test
```

### 4.3 Update Existing Tests
**Files**: `tests/unit/test_cli_commands_*.py`
- [ ] Remove any Hydra-related test cases
- [ ] Simplify mock-heavy tests
- [ ] Focus on testing actual functionality

## Phase 5: Update Documentation

### 5.1 Update CLI Documentation
- [ ] Remove all Hydra-related documentation
- [ ] Update command examples to use simple syntax
- [ ] Remove Hydra configuration examples

### 5.2 Update README
- [ ] Remove Hydra installation instructions
- [ ] Update usage examples
- [ ] Simplify getting started guide

### 5.3 Update Examples
- [ ] Remove Hydra-specific examples
- [ ] Create simple petal file examples
- [ ] Update demo scripts

## Phase 6: Dependency Cleanup

### 6.1 Update pyproject.toml ✅ **COMPLETED**
```toml
# These dependencies have been removed:
# hydra-core = "^1.3.2" ✅ REMOVED
# omegaconf = "^2.3.0" ✅ REMOVED (was only used by Hydra)
```

### 6.2 Update requirements.txt
- [ ] Remove Hydra-related packages
- [ ] Keep only essential dependencies

### 6.3 Update Development Dependencies
- [ ] Remove any Hydra-related dev dependencies
- [ ] Update test dependencies if needed

## Phase 7: Validation and Testing

### 7.1 Run Full Test Suite
- [ ] Ensure all tests pass after Hydra removal
- [ ] Fix any broken tests
- [ ] Verify no Hydra imports remain

### 7.2 Test CLI Commands
- [ ] Test `lily compose <file>` works
- [ ] Test `lily info [file]` works
- [ ] Test error handling works correctly
- [ ] Test help messages are clear

### 7.3 Test Examples
- [ ] Ensure example petal files still work
- [ ] Test demo scripts
- [ ] Verify documentation examples work

## Phase 8: Final Cleanup

### 8.1 Code Review
- [ ] Search for any remaining Hydra references
- [ ] Remove any unused imports
- [ ] Clean up any dead code

### 8.2 Documentation Review
- [ ] Ensure all documentation is updated
- [ ] Remove any outdated references
- [ ] Update any configuration examples

### 8.3 Commit and Tag
- [ ] Create comprehensive commit message
- [ ] Tag the release if appropriate
- [ ] Update changelog

## Success Criteria

### Functional Requirements
- [ ] All CLI commands work without Hydra
- [ ] All tests pass
- [ ] No Hydra dependencies in project
- [ ] Simple, clear command interface

### Code Quality
- [ ] No Hydra imports anywhere in codebase
- [ ] Clean, simple error handling
- [ ] Testable code without complex mocking
- [ ] Clear, maintainable structure

### User Experience
- [ ] Simple command syntax: `lily compose file.petal`
- [ ] Clear error messages
- [ ] Helpful documentation
- [ ] No confusion about configuration

## Rollback Plan

If issues arise during removal:
1. **Immediate**: Revert to previous commit
2. **Partial**: Keep core petal system, remove only Hydra CLI
3. **Gradual**: Remove Hydra in phases, test each phase

## Timeline Estimate

- **Phase 1-2**: 2-3 hours (identification and core removal)
- **Phase 3**: 1-2 hours (CLI simplification)
- **Phase 4**: 2-3 hours (test rewriting)
- **Phase 5-6**: 1 hour (documentation and dependencies)
- **Phase 7-8**: 1-2 hours (validation and cleanup)

**Total**: 7-11 hours of focused work

## Notes

- This plan assumes the core petal system is sound (which it appears to be)
- Focus on simplicity and testability
- Remove complexity, not functionality
- Keep the good parts (petal format, composition engine)
- Make the interface clean and intuitive

The goal is to end up with a simple, clean, testable codebase that does exactly what users need without unnecessary complexity.
