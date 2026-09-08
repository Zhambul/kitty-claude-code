# Copyright (c) 2026 Zhambyl Yermagambet
"""Check environment values passed to terminal launches."""

import pytest

from app import harness_environment
from terminal.launch import launch_tab_request
from terminal.models.tabs import EnvironmentVariable
from tests.plugin_tests import vocabulary as fixture


def test_terminal_launches_receive_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify terminal launches receive the configured environment."""
    monkeypatch.setenv(fixture.DASHBOARD_PORT_ENV, fixture.DASHBOARD_PORT_TEXT)
    monkeypatch.setenv("PATH", "/test/bin:/usr/bin:/bin")

    assert harness_environment.launch_environment() == (
        EnvironmentVariable(fixture.DASHBOARD_PORT_ENV, fixture.DASHBOARD_PORT_TEXT),
        EnvironmentVariable("PATH", "/test/bin:/usr/bin:/bin"),
    )


def test_direct_terminal_launch_rejects_invalid() -> None:
    """Verify direct terminal launch rejects invalid environment names."""
    with pytest.raises(ValueError, match="invalid environment variable name: 'bad name'"):
        launch_tab_request(
            fixture.WORK_PATH,
            ("harness-cli",),
            environment=(EnvironmentVariable("bad name", "x"),),
        )
