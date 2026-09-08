# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard lifecycle."""

import contextlib
import os
import signal
import subprocess  # noqa: S404 -- Start the local dashboard and the macOS browser command.
import sys
import time

from audit import record
from audit.documents import PathAudit
from dashboard.cli_health import holder, url
from dashboard.cli_health_values import STARTUP_ATTEMPTS, STARTUP_POLL_SECONDS
from dashboard.cli_output import _error, _output
from dashboard.cli_start_path import dashboard_entry


def start(flags: list[str] | None = None) -> int:
    """Start start.

    Returns:
        Integer result.

    """
    if holder():
        _output(f"dashboard already running · {url()}")
        return 0
    # module resolves the DATA DIRECTORY at import, which pulls the port contract
    # with it. Imported here rather than at the top so `main` has already applied
    # `--port` and `--data-dir` to the environment those two read — a constant
    # frozen before the flags were parsed is a flag that silently does nothing,
    # measured: `serve --port 8794` bound 8377 and died on the busy port.

    entry = dashboard_entry()
    command = [sys.executable, entry, "serve", *(flags or [])]
    try:
        process = subprocess.Popen(  # noqa: S603 -- Use this Python executable and the local dashboard entry without a shell.
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        record.error("", "spawn web dashboard", PathAudit(path=entry))
        _error("dashboard failed to spawn (see audit errors)")
        return 1
    record.spawn("", process.pid, command[1:], purpose="web dashboard")
    for _ in range(STARTUP_ATTEMPTS):  # ~2s for the port to answer
        if holder():
            _output(f"dashboard started · {url()}")
            return 0
        if process.poll() is not None:
            _error(f"dashboard exited before it became ready (exit {process.returncode}; check logs)")
            return 1
        time.sleep(STARTUP_POLL_SECONDS)
    _error(f"dashboard startup is not confirmed (pid {process.pid}; check status and logs)")
    return 1


def stop() -> int:
    """Stop stop.

    Returns:
        Integer result.

    """
    pid = holder()
    if not pid:
        _output("dashboard not running")
        return 0
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError as error:
        _error(f"stop failed: {error}")
        return 1
    else:
        _output(f"dashboard stopped (pid {int(pid)})")
        return 0


def status() -> int:
    """Return the status.

    Returns:
        Status.

    """
    pid = holder()
    if pid:
        _output(f"running · pid {int(pid)} · {url()}")
    else:
        _output("not running")
    return 0


def open_browser() -> int:
    """Open browser.

    Returns:
        Integer result.

    """
    rc = start()
    if rc:
        return rc
    with contextlib.suppress(OSError):
        subprocess.run(["/usr/bin/open", url()], check=False)  # noqa: S603 -- Pass the dashboard URL to the system macOS command without a shell.
    return 0
