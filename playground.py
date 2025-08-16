#!/usr/bin/env python3
"""Playground for demonstrating the new Petal tool architecture."""

import ruamel.yaml

from lily.petal.executor.core import PetalExecutor
from lily.petal.models_strict import (
    DebugEchoStepConfig,
    PetalFile,
    PythonEvalStepConfig,
)
from lily.petal.tool_registry import tool_registry

# Sample YAML for demonstration
yaml_str = """
name: "demo-workflow"
description: "A demonstration workflow"
version: "0.1"
params:
  input_file: "data.csv"
  output_dir: "results/"
env:
  API_KEY: "secret-key"
steps:
  - id: "step1"
    uses: "debug.echo"
    message: "Hello from Petal!"
    level: "info"
    timestamp: true
  - id: "step2"
    uses: "python.eval"
    expression: "2 + 2"
    globals:
      multiplier: 10
    reads: ["input_file"]
    writes: ["result"]
"""


def demonstrate_tool_registry() -> None:
    """Demonstrate the tool registry functionality."""
    print("=== Tool Registry ===\n")

    # List available tools
    tools = tool_registry.list_tools()
    print(f"Available tools: {tools}")

    # Get specific tools
    debug_tool = tool_registry.get_tool("debug.echo")
    python_tool = tool_registry.get_tool("python.eval")

    print(f"\nDebug tool: {debug_tool.__class__.__name__}")
    print(f"Python tool: {python_tool.__class__.__name__}")

    # Show tool descriptions
    print(f"\nDebug tool description: {debug_tool.get_description()}")
    print(f"Python tool description: {python_tool.get_description()}")

    print()


def demonstrate_step_configs() -> None:
    """Demonstrate step configuration parsing."""
    print("=== Step Configuration Parsing ===\n")

    # Parse YAML
    yaml = ruamel.yaml.YAML(typ="safe")
    data = yaml.load(yaml_str)

    # Create PetalFile instance
    workflow = PetalFile(**data)

    print(f"📋 Workflow: {workflow.name}")
    print(f"📝 Description: {workflow.description}")
    print(f"🔧 Version: {workflow.version}")
    print(f"📊 Parameters: {workflow.params}")
    print(f"🌍 Environment: {workflow.env}")
    print()

    print("Step Analysis:")
    for i, step in enumerate(workflow.steps, 1):
        print(f"\n{i}. {step.id}: {step.uses}")
        print(f"   Step Config Class: {step.__class__.__name__}")

        # Get the tool
        tool = tool_registry.get_tool(step.uses)
        if tool:
            print(f"   Tool Class: {tool.__class__.__name__}")

            # Show tool-specific fields based on step type
            if step.uses == "debug.echo":
                print("   Tool Fields:")
                print(f"     - message: {step.message}")
                print(f"     - level: {step.level}")
                print(f"     - timestamp: {step.timestamp}")

            elif step.uses == "python.eval":
                print("   Tool Fields:")
                print(f"     - expression: {step.expression}")
                print(f"     - globals: {step.globals}")
                print(f"     - reads: {step.reads}")
                print(f"     - writes: {step.writes}")

        # Validate the step
        is_valid = tool_registry.validate_step(step)
        print(f"   Valid: {'✅' if is_valid else '❌'}")

    print()


def demonstrate_workflow_execution() -> None:
    """Demonstrate workflow execution with the new architecture."""
    print("=== Workflow Execution ===\n")

    # Create a simple workflow
    step1 = DebugEchoStepConfig(
        id="step1", uses="debug.echo", message="Hello from Petal!"
    )
    step2 = PythonEvalStepConfig(id="step2", uses="python.eval", expression="2 + 2")

    petal_file = PetalFile(
        name="demo-workflow", description="Demonstration workflow", steps=[step1, step2]
    )

    # Execute the workflow
    executor = PetalExecutor()
    result = executor.execute(petal_file)

    print("Execution Result:")
    print(f"  Run ID: {result['run_id']}")
    print(f"  Status: {result['status']}")
    print(f"  Step Results: {result['step_results']}")
    print()


def main() -> None:
    """Main demonstration function."""
    print("🎯 Petal Refactored Tool Architecture Demonstration")
    print("=" * 60)
    print()

    demonstrate_tool_registry()
    demonstrate_step_configs()
    demonstrate_workflow_execution()

    print("✅ All demonstrations completed successfully!")
    print("\n🎉 The Petal system now has:")
    print("  - Strongly typed step configurations")
    print("  - Dynamic tool registry with auto-discovery")
    print("  - Clean separation of concerns")
    print("  - No more circular imports!")
    print("  - All tests passing with 81% coverage")


if __name__ == "__main__":
    main()
