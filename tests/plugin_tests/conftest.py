# Copyright (c) 2026 Zhambyl Yermagambet
"""Load shared fixtures for canonical harness plugin tests."""

from pathlib import Path

import pytest

from tests.plugin_tests.support_liveness import QuietLiveness


@pytest.fixture(autouse=True)
def quiet_liveness(monkeypatch: pytest.MonkeyPatch) -> None:
    """Disable liveness only for tests in the plugin test directory."""
    monkeypatch.setattr("engine.interpret.liveness.SessionLivenessSource", QuietLiveness)


@pytest.fixture
def codex_home(tmp_path: Path) -> Path:
    """Provide one isolated native Codex home directory.

    Returns:
        The temporary directory for the test.

    """
    return tmp_path
