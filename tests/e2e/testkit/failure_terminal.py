# Copyright (c) 2026 Zhambyl Yermagambet
"""Describe terminal state for an E2E failure report."""

from __future__ import annotations

from contextlib import closing
from typing import TYPE_CHECKING

from sdk.client import BaqylauClient
from tests.e2e.testkit import failure_processes, failure_storage, failure_values

if TYPE_CHECKING:
    from api.diagnostics.models import TerminalWindowDiagnosticResponse
    from tests.e2e.testkit.process import ApplicationProcess


def read_windows(application: ApplicationProcess) -> tuple[TerminalWindowDiagnosticResponse, ...]:
    """Read terminal diagnostic windows.

    Returns:
        The diagnostic windows.

    """
    with closing(BaqylauClient(application.endpoint.url)) as client:
        return client.diagnostics.terminal().windows


def process_values(window: TerminalWindowDiagnosticResponse) -> list[dict[str, failure_values.JsonValue]]:
    """Return renderable process values for one terminal window.

    Returns:
        The process values.

    """
    return [
        {
            "process_id": process.process_id,
            "command": process.command,
            "environment": (
                {} if process.process_id is None else failure_processes.selected_environment(process.process_id)
            ),
        }
        for process in window.processes
    ]


def state(application: ApplicationProcess, window_ids: frozenset[str] | None) -> str:
    """Describe terminal windows owned by an E2E scenario.

    Returns:
        The terminal report section.

    """
    try:
        windows = read_windows(application)
    except (OSError, RuntimeError, ValueError) as error:
        return f"terminal\n  read_error={type(error).__name__}: {error}"
    owned_window_ids = (
        failure_storage.stored_window_ids(application.config.data_directory)
        if window_ids is None
        else window_ids
    )
    windows = tuple(window for window in windows if str(window.window_id) in owned_window_ids)
    if not windows:
        return "terminal\n  windows=[]"
    lines = ["terminal"]
    for window in windows:
        lines.extend(
            (
                f"  window={window.window_id} processes={failure_values.compact(process_values(window))}",
                f"  screen={failure_values.compact(window.screen or window.screen_error or '')}",
            ),
        )
    return "\n".join(lines)
