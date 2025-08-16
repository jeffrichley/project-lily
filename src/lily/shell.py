"""Shell command execution for Lily."""

import subprocess
from pathlib import Path


def run_interactive_command(command: str, cwd: Path | None = None) -> int:
    """Run a command interactively (no output capture).

    Args:
        command: Command to run
        cwd: Working directory

    Returns:
        Exit code
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=False,
        )
        return result.returncode
    except KeyboardInterrupt:
        return 130
    except Exception:
        return 1
