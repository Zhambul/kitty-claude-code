# Copyright (c) 2026 Zhambyl Yermagambet
"""Check the dashboard port-owner lookup without querying live processes."""

from unittest.mock import Mock

import pytest

from core.daemon import contract
from dashboard import cli_health

LISTENER_PROCESS_ID = 123
LSOF_PATH = "/test/bin/lsof"


@pytest.fixture
def process_query(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace the health probe and process query with test responses.

    Returns:
        The process query mock.

    """
    monkeypatch.setattr(cli_health, "_answered_pid", Mock(return_value=0))
    monkeypatch.setattr(cli_health, "process_is_alive", Mock(return_value=True))
    monkeypatch.setattr("dashboard.cli_health.shutil.which", Mock(return_value=LSOF_PATH))
    query = Mock(return_value=Mock(stdout=f"{LISTENER_PROCESS_ID}\n"))
    monkeypatch.setattr("dashboard.cli_health.subprocess.run", query)
    return query


def test_lookup_uses_resolved_executable(process_query: Mock) -> None:
    """Pass fixed lsof options and the configured port as separate arguments."""
    assert cli_health.holder() == LISTENER_PROCESS_ID
    process_query.assert_called_once_with(
        [LSOF_PATH, "-nP", f"-iTCP:{contract.PORT_NUMBER}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        check=False,
        timeout=2,
    )


def test_lookup_without_lsof(process_query: Mock, monkeypatch: pytest.MonkeyPatch) -> None:
    """Return no owner when lsof is absent, without starting a process."""
    monkeypatch.setattr("dashboard.cli_health.shutil.which", Mock(return_value=None))
    assert cli_health.holder() == 0
    process_query.assert_not_called()


@pytest.mark.parametrize("output", ["", "not-a-process-id\n"])
def test_lookup_rejects_invalid_output(process_query: Mock, output: str) -> None:
    """Return no owner if the query has no numeric process identifier."""
    process_query.return_value.stdout = output
    assert cli_health.holder() == 0


def test_lookup_handles_process_error(process_query: Mock) -> None:
    """Return no owner if lsof cannot be started."""
    process_query.side_effect = OSError("process unavailable")
    assert cli_health.holder() == 0
