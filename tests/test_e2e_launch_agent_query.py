# Copyright (c) 2026 Zhambyl Yermagambet
"""Check the installed-daemon query without touching a live LaunchAgent."""

from unittest.mock import Mock

import pytest

from tests.e2e.testkit import restarts

USER_ID = 501
PROCESS_ID = 123


def test_launch_agent_query_uses_system_command(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read the fixed user LaunchAgent through the system command path."""
    query = Mock(return_value=Mock(
        returncode=0,
        stdout=f"state = running\npid = {PROCESS_ID}\nproperties = keepalive runatload\n",
    ))
    monkeypatch.setattr("tests.e2e.testkit.restarts.os.getuid", lambda: USER_ID)
    monkeypatch.setattr("tests.e2e.testkit.restarts.subprocess.run", query)
    restarts.InstalledDaemonRestart(new_process_id=PROCESS_ID).assert_automatic_launch_agent()
    query.assert_called_once_with(
        ("/bin/launchctl", "print", f"gui/{USER_ID}/{restarts.LAUNCH_AGENT_LABEL}"),
        check=False,
        capture_output=True,
        text=True,
    )


def test_launch_agent_query_reports_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Report a missing LaunchAgent without trying to start one."""
    query = Mock(return_value=Mock(returncode=1, stderr="not found"))
    monkeypatch.setattr("tests.e2e.testkit.restarts.subprocess.run", query)
    with pytest.raises(AssertionError, match="is unavailable: not found"):
        restarts.InstalledDaemonRestart().assert_automatic_launch_agent()
    query.assert_called_once()
