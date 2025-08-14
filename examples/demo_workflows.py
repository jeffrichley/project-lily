#!/usr/bin/env python3
"""
Demo script showing how to use Lily petal workflows with the simplified CLI.

This script demonstrates various petal workflow examples without any Hydra dependencies.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a command and display the result."""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.stdout:
            print("✅ Output:")
            print(result.stdout)
        if result.stderr:
            print("⚠️  Errors/Warnings:")
            print(result.stderr)
        print(f"Exit code: {result.returncode}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Run the demo workflows."""
    print("🚀 Lily Petal Workflow Demo")
    print("This demo shows how to use Lily's simplified CLI with petal files")

    # Get the examples directory
    examples_dir = Path(__file__).parent
    os.chdir(examples_dir)

    # Demo 1: Show help
    run_command("lily --help", "Show main CLI help")

    # Demo 2: Show compose command help
    run_command("lily compose --help", "Show compose command help")

    # Demo 3: Show info command help
    run_command("lily info --help", "Show info command help")

    # Demo 4: Info on hello world workflow
    run_command("lily info hello_world.petal", "Get info about hello world workflow")

    # Demo 5: Dry run of hello world workflow
    run_command(
        "lily compose hello_world.petal --dry-run", "Dry run hello world workflow"
    )

    # Demo 6: Info on data processing workflow
    run_command(
        "lily info data_processing.petal", "Get info about data processing workflow"
    )

    # Demo 7: Info on web scraping workflow
    run_command("lily info web_scraping.petal", "Get info about web scraping workflow")

    # Demo 8: Info on file backup workflow
    run_command("lily info file_backup.petal", "Get info about file backup workflow")

    # Demo 9: Info on test hierarchy workflow
    run_command(
        "lily info test_hierarchy.petal", "Get info about test hierarchy workflow"
    )

    # Demo 10: Info on video processing workflow
    run_command(
        "lily info video_processing.petal", "Get info about video processing workflow"
    )

    print(f"\n{'='*60}")
    print("🎉 Demo completed!")
    print("=" * 60)
    print("Key points:")
    print("• No Hydra configuration needed")
    print("• Simple CLI commands: lily compose <file>")
    print("• Easy workflow inspection: lily info <file>")
    print("• All examples use native petal format")
    print("• Clean, simple, and maintainable")


if __name__ == "__main__":
    main()
