# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata api git."""

from __future__ import annotations

import shutil
import subprocess  # noqa: S404 -- Create a local Git repository for the test.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

GIT_NOT_INSTALLED = "git is not installed"


def create_linked_worktree(source: Path, linked: Path) -> None:
    """Create an empty test repository and a linked worktree.

    Raises:
        FileNotFoundError: If Git is not installed.

    """
    executable = shutil.which("git")
    if executable is None:
        raise FileNotFoundError(GIT_NOT_INSTALLED)
    source.mkdir()
    commands = (
        ("init", "--initial-branch=main"),
        ("config", "user.name", "Baqylau Test"),
        ("config", "user.email", "baqylau@example.invalid"),
        ("commit", "--allow-empty", "-m", "initial"),
        ("worktree", "add", "-b", "worktree", str(linked)),
    )
    for arguments in commands:
        subprocess.run(  # noqa: S603 -- Run the fixed test commands with path arguments, without a shell.
            (executable, "-C", str(source), *arguments),
            check=True,
            capture_output=True,
            text=True,
        )
