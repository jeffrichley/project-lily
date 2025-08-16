#!/usr/bin/env python3
"""
Demo script showing basic Lily functionality.

This script demonstrates various Lily features without any complex dependencies.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> None:
    """Run a command and display the result."""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"💻 Command: {command}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
        )

        if result.stdout:
            print("✅ Output:")
            print(result.stdout)

        if result.stderr:
            print("⚠️  Errors:")
            print(result.stderr)

        print(f"Exit code: {result.returncode}")

    except Exception as e:
        print(f"❌ Error running command: {e}")


def main():
    """Run the Lily demo."""
    print("🚀 Lily Demo")
    print("This demo shows basic Lily functionality")
    print("=" * 60)

    # Check if lily is installed
    try:
        result = subprocess.run(
            ["uv", "run", "lily", "--help"], capture_output=True, text=True, check=True
        )
        print("✅ Lily CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Lily CLI not found. Please install Lily first.")
        print("Run: uv pip install -e .")
        sys.exit(1)

    # Demo basic commands
    run_command("uv run lily --help", "Show Lily help")
    run_command("uv run lily version", "Show Lily version")

    # Demo configuration
    run_command("uv run lily config", "Show configuration management")

    # Demo start command
    print("\n" + "=" * 60)
    print("🌙 Interactive Shell Demo")
    print("=" * 60)
    print("The 'uv run lily start' command launches an interactive shell.")
    print("This would allow you to:")
    print("• Execute commands interactively")
    print("• Manage configuration")
    print("• Use built-in utilities")
    print("• Navigate the file system")
    print("\n(Not running interactively in this demo)")

    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("=" * 60)
    print("Lily provides a clean, modern CLI for development tasks.")
    print("Key features:")
    print("• Simple command interface")
    print("• Configuration management")
    print("• Interactive shell")
    print("• Extensible architecture")


if __name__ == "__main__":
    main()
