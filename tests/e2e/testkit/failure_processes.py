# Copyright (c) 2026 Zhambyl Yermagambet
"""Read process state for E2E failure reports."""

from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

import psutil

from tests.e2e.testkit import failure_values

if TYPE_CHECKING:
    from tests.e2e.testkit.process import ApplicationProcess


def _record_system_process(
    process: psutil.Process,
    process_counts: dict[str, int],
    e2e_daemons: list[tuple[int, str]],
) -> None:
    try:
        process_name, command = (
            (process.info["name"] or "").lower(),
            tuple(process.info["cmdline"] or ()),
        )
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return
    for process_kind in process_counts:
        if process_kind in process_name:
            process_counts[process_kind] += 1
    if "python" not in process_name or not any("spawn_main" in argument for argument in command):
        return
    try:
        parent = process.parent()
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return
    if parent is not None:
        e2e_daemons.append((process.pid, f"parent:{parent.pid}"))


def system_state() -> str:
    """Return host state for an E2E failure report.

    Returns:
        Host state for an E2E failure report.

    """
    names = {"claude": 0, "codex": 0, "python": 0}
    e2e_daemons: list[tuple[int, str]] = []
    for process in psutil.process_iter(("name", "cmdline")):
        _record_system_process(process, names, e2e_daemons)
    load_average = tuple(round(load_value, 2) for load_value in os.getloadavg())
    available_memory = psutil.virtual_memory().available // (1024 * 1024)
    return (
        "system\n"
        f"  load={load_average}\n"
        f"  available_memory_mb={available_memory}\n"
        f"  process_counts={names}\n"
        f"  e2e_daemons={e2e_daemons}"
    )


def application_state(application: ApplicationProcess) -> str:
    """Return application process state for an E2E failure report.

    Returns:
        Application process state for an E2E failure report.

    """
    process = application.process
    endpoint = application.endpoint
    data_directory = application.config.data_directory
    lines = [
        "application",
        f"  endpoint={endpoint.host}:{endpoint.port}",
        f"  pid={process.pid} alive={process.is_alive()} exit_code={process.exitcode}",
        f"  data_directory={data_directory}",
    ]
    if process.pid is None:
        return "\n".join(lines)
    try:
        lines.extend(_related_process_lines(process.pid))
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as error:
        lines.append(f"  process_read_error={error}")
        return "\n".join(lines)
    return "\n".join(lines)


def _related_process_lines(process_id: int) -> tuple[str, ...]:
    root_process = psutil.Process(process_id)
    related = (root_process, *root_process.children(recursive=True))
    now = time.time()
    return tuple(f"  {_process_line(process, now)}" for process in related)


def _process_line(process: psutil.Process, now: float) -> str:
    try:
        return _process_description(process, now)
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as error:
        return f"process pid={process.pid} read_error={error}"


def _process_description(process: psutil.Process, now: float) -> str:
    memory_megabytes = process.memory_info().rss // (1024 * 1024)
    descriptor_count = process.num_fds() if hasattr(process, "num_fds") else -1
    return (
        f"process pid={process.pid} name={process.name()!r} status={process.status()} "
        f"parent={process.ppid()} age_seconds={round(now - process.create_time(), 1)} "
        f"cpu_seconds={round(sum(process.cpu_times()), 2)} "
        f"threads={process.num_threads()} fds={descriptor_count} memory_mb={memory_megabytes} "
        f"command={failure_values.compact(process.cmdline())} "
        f"environment={failure_values.compact(selected_environment(process.pid))}"
    )


def selected_environment(process_id: int) -> dict[str, str]:
    """Return visible environment values for one process.

    Returns:
        Visible environment values for one process.

    """
    try:
        environment = psutil.Process(process_id).environ()
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
        return {}
    visible_names = (
        "BAQYLAU_DASHBOARD_PORT",
        "CODEX_HOME",
        "CLAUDE_CONFIG_DIR",
        "CLAUDE_CODE_MANAGED_SETTINGS_PATH",
    )
    return {name: environment[name] for name in visible_names if name in environment}
