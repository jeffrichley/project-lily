# Lily Examples

This directory contains example petal workflow files that demonstrate how to use Lily's simplified workflow automation system.

## Overview

All examples use the native petal format without any external configuration dependencies. The examples show various use cases and patterns for creating workflows.

## Available Examples

### Basic Examples

- **`hello_world.petal`** - Simple greeting workflow with parameter substitution
- **`test_hierarchy.petal`** - Test workflow demonstrating hierarchical configuration

### Real-World Examples

- **`data_processing.petal`** - CSV data processing workflow with batch processing
- **`web_scraping.petal`** - Web content scraping workflow with retry logic
- **`file_backup.petal`** - File and directory backup workflow with compression
- **`video_processing.petal`** - Complex video processing workflow with multiple steps

## Running Examples

### Using the CLI

```bash
# Get information about a workflow
lily info examples/hello_world.petal

# Dry run a workflow (see what would happen)
lily compose examples/hello_world.petal --dry-run

# Execute a workflow
lily compose examples/hello_world.petal
```

### Demo Script

Run the demo script to see all examples in action:

```bash
cd examples
python demo_workflows.py
```

## Example Structure

Each petal file follows this structure:

```yaml
petal: "1"
name: "Workflow Name"
description: "Workflow description"

params:
  # Input parameters with types and validation

vars:
  # Computed variables

steps:
  - id: "step_name"
    uses: "step_type"
    needs: ["dependencies"]
    with_:
      # Step-specific configuration
    outputs:
      # Step outputs

outputs:
  # Workflow outputs
```

## Key Features Demonstrated

- **Parameter validation** - Required parameters with types and help text
- **Variable substitution** - Dynamic values using template syntax
- **Step dependencies** - Sequential and parallel execution
- **Output handling** - Structured output from steps and workflows
- **Error handling** - Validation and error checking
- **Environment variables** - Shell environment configuration

## Migration from Hydra

These examples have been simplified from the previous Hydra-based configuration system:

- ❌ No complex configuration hierarchies
- ❌ No external YAML configuration files
- ❌ No Hydra-specific syntax
- ✅ Simple, direct petal files
- ✅ Clear parameter definitions
- ✅ Easy to understand and maintain

## Getting Started

1. Start with `hello_world.petal` to understand the basics
2. Try `data_processing.petal` for a more complex example
3. Use `lily info <file>` to inspect workflow details
4. Use `lily compose <file> --dry-run` to test workflows safely

## Contributing

When adding new examples:

- Keep them focused on a specific use case
- Include clear parameter documentation
- Use realistic but simple scenarios
- Ensure they work without external dependencies
- Test with both `lily info` and `lily compose --dry-run`
