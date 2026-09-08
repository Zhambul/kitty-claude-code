# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard health."""

import shutil
import subprocess  # noqa: S404 -- Query the local process that holds the dashboard port.
from http import HTTPStatus, client as http_client
from types import ModuleType

from core.process import process_is_alive
from dashboard.cli_health_values import HEALTH_PATH, HEALTH_REQUEST_ERRORS, HEALTH_TIMEOUT_SECONDS
from dashboard.cli_models import HealthProcess


def holder() -> int:
    """Return the holder.

    The running server's pid, or 0.

        Asked over the port the daemon binds, because that bind IS the singleton
        guard — a pid claim in a database was a second answer to the same question,
        and it could disagree.

        Anything other than a pid falls through to `_listening_pid`, which asks the
        kernel who holds the port. That covers the two cases the probe cannot: a
        daemon wedged past answering, and — measured, the first time this shipped —
        a daemon still running the code from BEFORE /api/health existed, which
        answers the probe with a 404. Both are exactly the daemon you need `stop`
        for, and reporting "not running" at one is how you end up with two.

    Returns:
        Holder.

    """
    from core.daemon import contract as daemon_contract  # noqa: PLC0415 — same import purity as _serve()

    pid = _answered_pid(daemon_contract) or _listening_pid(daemon_contract.PORT_NUMBER)
    return pid if pid and process_is_alive(pid) else 0


def _answered_pid(daemon_contract: ModuleType) -> int:
    """Return the answered PID.

    The pid the daemon reports for itself, or 0 if it does not report one.

    Returns:
        Answered PID.

    """
    connection = http_client.HTTPConnection(
        daemon_contract.HOST_ADDRESS,
        daemon_contract.PORT_NUMBER,
        timeout=HEALTH_TIMEOUT_SECONDS,
    )
    try:
        return _health_process_id(connection)
    except HEALTH_REQUEST_ERRORS:
        return 0
    finally:
        connection.close()


def _health_process_id(connection: http_client.HTTPConnection) -> int:
    connection.request("GET", HEALTH_PATH)
    response = connection.getresponse()
    if response.status != HTTPStatus.OK:
        return 0
    return HealthProcess.model_validate_json(response.read()).process_id


def _listening_pid(port: int) -> int:
    """Return the listening PID.

    Whoever holds the port, when it no longer answers. Best effort: if lsof
        is not installed there is nothing to signal and nothing to report.

    Returns:
        Listening PID.

    """
    executable = shutil.which("lsof")
    if executable is None:
        return 0
    try:
        found = subprocess.run(  # noqa: S603 -- Use the resolved lsof path and fixed options with an integer port.
            [executable, "-nP", f"-iTCP:{int(port)}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return 0
    first = found.stdout.split()
    if first and first[0].isdigit():
        return int(first[0])
    return 0


def url() -> str:
    # the daemon contract, not the server facade: the bind address is
    # core/daemon/contract.py's to own, and a lazy import keeps this module import-pure
    # like _serve() does (the application runtime owns the server import).
    """Return the URL.

    Returns:
        URL.

    """
    from core.daemon import contract as daemon_contract  # noqa: PLC0415 — same import purity as _serve()

    return f"http://{daemon_contract.HOST_ADDRESS}:{int(daemon_contract.PORT_NUMBER)}"
