# Copyright (c) 2026 Zhambyl Yermagambet
"""Pure ownership checks for one terminal metadata snapshot."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from terminal.models.values import WindowInfo, WindowProcess


def _process_matches(window_process: WindowProcess, process_name: str) -> bool:
    command = window_process.command
    return bool(command) and Path(command[0]).name == process_name


def window_hosts_process(
    window_info: WindowInfo,
    process_id: int | None,
    process_name: str,
) -> bool:
    """Return true when the window reports the specified foreground process.

    Returns:
        True when the window reports the specified foreground process.

    """
    if process_id is not None:
        return any(process.process_id == process_id for process in window_info.processes)
    return any(_process_matches(process, process_name) for process in window_info.processes)
