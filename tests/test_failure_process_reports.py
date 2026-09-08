# Copyright (c) 2026 Zhambyl Yermagambet
"""Check process reports when application process details are unavailable."""

from unittest.mock import Mock

import psutil
import pytest

from tests.e2e.testkit.failure_processes import application_state

PROCESS_ID = 17
APPLICATION_PORT = 8377


def test_report_before_process_start() -> None:
    """Keep the endpoint and data directory before a process has a PID."""
    application = Mock(
        process=Mock(pid=None, exitcode=None, is_alive=Mock(return_value=False)),
        endpoint=Mock(host="127.0.0.1", port=APPLICATION_PORT),
        config=Mock(data_directory="/test-data"),
    )
    assert application_state(application) == (
        "application\n"
        "  endpoint=127.0.0.1:8377\n"
        "  pid=None alive=False exit_code=None\n"
        "  data_directory=/test-data"
    )


def test_report_after_process_disappears(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep application details when the native process lookup fails."""
    application = Mock(
        process=Mock(pid=PROCESS_ID, exitcode=0, is_alive=Mock(return_value=False)),
        endpoint=Mock(host="127.0.0.1", port=APPLICATION_PORT),
        config=Mock(data_directory="/test-data"),
    )
    error = psutil.NoSuchProcess(PROCESS_ID)
    monkeypatch.setattr(psutil, "Process", Mock(side_effect=error))
    assert application_state(application) == (
        "application\n"
        "  endpoint=127.0.0.1:8377\n"
        f"  pid={PROCESS_ID} alive=False exit_code=0\n"
        "  data_directory=/test-data\n"
        f"  process_read_error={error}"
    )
