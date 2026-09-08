# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for terminal resolution."""

from __future__ import annotations

import pytest

from terminal.impl.resolution import resolve

TERMINAL_ENVIRONMENT = "BAQYLAU_TERMINAL"


def test_terminal_is_detected_and_pinned_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify terminal selection uses its configured name."""
    monkeypatch.setenv(TERMINAL_ENVIRONMENT, "none")
    terminal = resolve()
    assert terminal is not None
    assert terminal.name == "none"
    monkeypatch.setenv(TERMINAL_ENVIRONMENT, "pty")
    terminal = resolve()
    assert terminal is not None
    assert terminal.name == "pty"
    monkeypatch.setenv(TERMINAL_ENVIRONMENT, "nothing-like-it")
    with pytest.raises(ValueError, match="unsupported terminal"):
        resolve()
    monkeypatch.delenv(TERMINAL_ENVIRONMENT)
    monkeypatch.setattr("terminal.impl.kitty.remote.shutil.which", lambda _name: None)
    monkeypatch.setattr("terminal.impl.kitty.remote.os.access", lambda _path, _mode: False)
    monkeypatch.delenv("KITTY_KITTEN_BIN", raising=False)
    assert resolve() is None
