# Copyright (c) 2026 Zhambyl Yermagambet
"""Check the dashboard entry and confirmed startup."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from dashboard import cli_lifecycle
from dashboard.cli_start_path import dashboard_entry

STARTED_PROCESS_ID = 123


def test_dashboard_start_uses_a_python_entry() -> None:
    """Do not pass the shell wrapper to Python."""
    entry = Path(dashboard_entry())
    assert entry.suffix == ".py"
    compile(entry.read_text(encoding="utf-8"), str(entry), "exec")  # noqa: WPS421 -- Validate the entry as Python without executing it.


def _startup_process(monkeypatch: pytest.MonkeyPatch, state: str) -> Mock:
    process = Mock(pid=STARTED_PROCESS_ID, returncode=1)
    process.poll.return_value = 1 if state == "exited" else None
    monkeypatch.setattr("dashboard.cli_lifecycle.subprocess.Popen", Mock(return_value=process))
    monkeypatch.setattr("dashboard.cli_lifecycle.record.spawn", Mock())
    monkeypatch.setattr(cli_lifecycle, "STARTUP_ATTEMPTS", 1)
    monkeypatch.setattr("dashboard.cli_lifecycle.time.sleep", Mock())
    monkeypatch.setattr(
        cli_lifecycle, "holder",
        Mock(side_effect=[None, STARTED_PROCESS_ID if state == "ready" else None]),
    )
    return process


@pytest.mark.parametrize("state", ["ready", "exited", "unconfirmed"])
def test_start_requires_health_check(monkeypatch: pytest.MonkeyPatch, state: str) -> None:
    """Do not report a dead or unconfirmed child as started."""
    process = _startup_process(monkeypatch, state)
    output = Mock()
    error = Mock()
    monkeypatch.setattr(cli_lifecycle, "_output", output)
    monkeypatch.setattr(cli_lifecycle, "_error", error)

    result = cli_lifecycle.start()

    if state == "ready":
        assert result == 0
        output.assert_called_once()
        error.assert_not_called()
    else:
        assert result == 1
        output.assert_not_called()
        error.assert_called_once()
    process.terminate.assert_not_called()
