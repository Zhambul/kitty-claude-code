# Copyright (c) 2026 Zhambyl Yermagambet
"""Run Git commands inside an isolated repository fixture."""

from __future__ import annotations

import shutil
import subprocess  # noqa: S404 -- Prepare and change isolated Git repositories for E2E cases.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def run(working_directory: Path, *arguments: str) -> None:
    """Resolve Git and run one fixture command.

    Git command failures propagate to the test.

    Raises:
        FileNotFoundError: If Git is not installed.

    """
    executable = shutil.which("git")
    if executable is None:
        message = "git is not installed"
        raise FileNotFoundError(message)
    subprocess.run(  # noqa: S603 -- Use the resolved Git path with separate fixture arguments, without a shell.
        (executable, "-C", str(working_directory), *arguments),
        check=True,
        capture_output=True,
        text=True,
    )
