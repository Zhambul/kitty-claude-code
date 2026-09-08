# Copyright (c) 2026 Zhambyl Yermagambet
"""Find Claude Code configuration directories."""

import os
from pathlib import Path


def claude_dirs(
    config: str,
    start: str | None = None,
    *,
    nearest_only: bool = False,
    env_pin: bool = True,
) -> list[str]:
    """Return project and user configuration directories.

    Returns:
        Configuration directories in precedence order.

    """
    directories = []
    project_directory = (os.environ.get("CLAUDE_PROJECT_DIR") or "").strip() if env_pin else ""
    if project_directory:
        project_config = Path(project_directory) / ".claude"
        if project_config.is_dir():
            directories.append(str(project_config))
    else:
        directories.extend(
            _ancestor_claude_dirs(start, nearest_only=nearest_only),
        )
    if config not in directories:
        directories.append(config)
    return directories


def _ancestor_claude_dirs(start: str | None, *, nearest_only: bool) -> list[str]:
    directories: list[str] = []
    current = Path(start).resolve() if start else Path.cwd()
    home = Path.home()
    while current not in {current.parent, home}:
        project_configuration = current / ".claude"
        if project_configuration.is_dir():
            directories.append(str(project_configuration))
            if nearest_only:
                break
        current = current.parent
    return directories
