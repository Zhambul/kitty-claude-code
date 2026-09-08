# Copyright (c) 2026 Zhambyl Yermagambet
"""Check clipboard guard commands without touching the system clipboard."""

from unittest.mock import Mock, call

import pytest

from harness.impl.claude_code.controls import clipboard_image


def test_image_guard_uses_system_applescript(monkeypatch: pytest.MonkeyPatch) -> None:
    """Read the clipboard format and clear an image with fixed commands."""
    monkeypatch.setattr("harness.impl.claude_code.controls.clipboard_image.platform.system", lambda: "Darwin")
    run = Mock(return_value=Mock(stdout="PNGf"))
    monkeypatch.setattr("harness.impl.claude_code.controls.clipboard_image.subprocess.run", run)
    assert clipboard_image.clear_image()
    assert run.call_args_list == [
        call(
            ["/usr/bin/osascript", "-e", "clipboard info"],
            capture_output=True, check=False, text=True, timeout=2,
        ),
        call(
            ["/usr/bin/osascript", "-e", 'set the clipboard to ""'],
            capture_output=True, timeout=2, check=True,
        ),
    ]


def test_image_guard_skips_other_platforms(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not start AppleScript on a non-macOS platform."""
    monkeypatch.setattr("harness.impl.claude_code.controls.clipboard_image.platform.system", lambda: "Linux")
    run = Mock()
    monkeypatch.setattr("harness.impl.claude_code.controls.clipboard_image.subprocess.run", run)
    assert not clipboard_image.clear_image()
    run.assert_not_called()
