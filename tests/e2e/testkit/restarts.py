# Copyright (c) 2026 Zhambyl Yermagambet
"""A typed boundary for the installed macOS daemon."""

from __future__ import annotations

import json
import os
import signal
import subprocess  # noqa: S404 -- Query the installed macOS LaunchAgent during E2E checks.
from dataclasses import dataclass
from urllib import error as urllib_error, request as urllib_request

from sdk.client import wait_for

HEALTH_URL = "http://127.0.0.1:8377/api/health"
LAUNCH_AGENT_LABEL = "top.zhambyl.baqylau-dashboard"
RESTART_TIMEOUT_SECONDS = 20.0
RESTART_POLL_SECONDS = 0.25


def _health_process_id() -> int | None:
    try:
        with urllib_request.urlopen(HEALTH_URL, timeout=1.0) as response:
            document = json.loads(response.read())
    except (OSError, urllib_error.URLError, json.JSONDecodeError):
        return None
    process_id = document.get("process_id") if isinstance(document, dict) else None
    return process_id if isinstance(process_id, int) and process_id > 1 else None


def _launch_agent_state() -> str:
    user_id = os.getuid()
    result = subprocess.run(  # noqa: S603 -- Use the system launchctl with a fixed label and numeric user ID.
        (
            "/bin/launchctl",
            "print",
            f"gui/{user_id}/{LAUNCH_AGENT_LABEL}",
        ),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        error_text = result.stderr.strip()
        message = f"launch agent {LAUNCH_AGENT_LABEL!r} is unavailable: {error_text}"
        raise AssertionError(message)
    return result.stdout


@dataclass
class InstalledDaemonRestart:
    """Represent installed daemon restart."""

    old_process_id: int | None = None
    new_process_id: int | None = None

    def stop_and_wait_for_replacement(self) -> None:
        """Stop the installed daemon and wait for its replacement process.

        Raises:
            AssertionError: If the health endpoint has no valid process identifier.

        """
        process_id = _health_process_id()
        if process_id is None:
            message = "the installed dashboard health endpoint is unavailable"
            raise AssertionError(message)
        self.old_process_id = process_id
        os.kill(process_id, signal.SIGTERM)
        self.new_process_id = wait_for(
            f"installed daemon process {process_id} to be replaced",
            self._replacement,
            timeout=RESTART_TIMEOUT_SECONDS,
            interval=RESTART_POLL_SECONDS,
        )

    def assert_new_process(self) -> None:
        """Process assert new process."""
        assert self.old_process_id is not None
        assert self.new_process_id is not None
        assert self.new_process_id != self.old_process_id
        assert _health_process_id() == self.new_process_id

    def assert_automatic_launch_agent(self) -> None:
        """Process assert automatic launch agent."""
        state = _launch_agent_state()
        assert "state = running" in state
        assert f"pid = {self.new_process_id}" in state
        properties = next(
            (line.strip() for line in state.splitlines() if line.strip().startswith("properties =")),
            "",
        )
        assert "keepalive" in properties
        assert "runatload" in properties

    def _replacement(self) -> int | None:
        process_id = _health_process_id()
        return process_id if process_id is not None and process_id != self.old_process_id else None
