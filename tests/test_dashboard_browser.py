# Copyright (c) 2026 Zhambyl Yermagambet
"""Check browser commands without starting the dashboard or a browser."""

from unittest.mock import Mock

import pytest

from dashboard import cli_lifecycle

DASHBOARD_URL = "http://127.0.0.1:8377"


@pytest.fixture
def browser_command(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace dashboard startup and the browser command.

    Returns:
        The browser command probe.

    """
    command = Mock()
    monkeypatch.setattr(cli_lifecycle, "start", Mock(return_value=0))
    monkeypatch.setattr(cli_lifecycle, "url", Mock(return_value=DASHBOARD_URL))
    monkeypatch.setattr("dashboard.cli_lifecycle.subprocess.run", command)
    return command


def test_browser_uses_system_command(browser_command: Mock) -> None:
    """Pass the dashboard URL to the absolute macOS command path."""
    assert cli_lifecycle.open_browser() == 0
    browser_command.assert_called_once_with(["/usr/bin/open", DASHBOARD_URL], check=False)


def test_browser_skips_failed_start(monkeypatch: pytest.MonkeyPatch, browser_command: Mock) -> None:
    """Do not open a browser when dashboard startup fails."""
    monkeypatch.setattr(cli_lifecycle, "start", Mock(return_value=1))
    assert cli_lifecycle.open_browser() == 1
    browser_command.assert_not_called()


def test_browser_allows_missing_system_command(browser_command: Mock) -> None:
    """Keep the dashboard available when the macOS command is absent."""
    browser_command.side_effect = FileNotFoundError
    assert cli_lifecycle.open_browser() == 0
    browser_command.assert_called_once()
