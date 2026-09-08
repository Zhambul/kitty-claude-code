# Copyright (c) 2026 Zhambyl Yermagambet
"""Build reports for failed and stalled E2E scenarios."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit import failure_processes, failure_profiles, failure_storage, failure_terminal

if TYPE_CHECKING:
    from pathlib import Path

    from tests.e2e.testkit.process import ApplicationProcess


def save_e2e_failure_diagnostics(application: ApplicationProcess, node_id: str, diagnostics: str) -> Path:
    """Save one complete failure report.

    Returns:
        The report path.

    """
    path = application.config.data_directory / "e2e-failure-report.txt"
    path.write_text(f"test={node_id}\n\n{diagnostics}\n", encoding="utf-8")
    return path


def e2e_failure_diagnostics(application: ApplicationProcess, window_ids: frozenset[str] | None = None) -> str:
    """Describe failed process, stored state, terminal, and profiles.

    Returns:
        The complete failure report.

    """
    sections = (
        failure_processes.system_state(),
        failure_processes.application_state(application),
        failure_terminal.state(application, window_ids),
        failure_profiles.state(application),
        failure_storage.database_state(application.config.data_directory),
    )
    return "\n\n".join(section for section in sections if section)


def e2e_stall_diagnostics(application: ApplicationProcess, window_ids: frozenset[str] | None = None) -> str:
    """Return the live-state part of a failure report.

    Returns:
        The live-state report.

    """
    return "\n\n".join(
        (
            failure_processes.system_state(),
            failure_processes.application_state(application),
            failure_terminal.state(application, window_ids),
            failure_profiles.state(application),
        ),
    )


def e2e_progress_marker(application: ApplicationProcess) -> tuple[int, int, int]:
    """Return counters that change when a scenario makes stored progress.

    Returns:
        The persistent progress counters.

    """
    return failure_storage.progress_marker(application.config.data_directory)
