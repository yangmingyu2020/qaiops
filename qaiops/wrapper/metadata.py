"""Metadata extraction for CLI wrapper."""

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def get_project_id() -> str | None:
    """Extract project ID from git repository root directory name.

    Returns None if not in a git repository.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip()).name
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_cwd() -> str:
    """Return the current working directory."""
    return os.getcwd()


def get_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()
