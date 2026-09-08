# Copyright (c) 2026 Zhambyl Yermagambet
"""Read terminal confirmation without starting a command process."""

from unittest.mock import Mock

import pytest

from terminal.impl.kitty.remote import GetTextRcPayload, KittyRcResponse, KittyRemote
from terminal.models.values import WindowId


@pytest.mark.parametrize("text", ["", "Ready for input"])
def test_screen_read_uses_socket(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    """Use the direct reply, including an empty screen."""
    remote = KittyRemote()
    raw = Mock(return_value=KittyRcResponse(ok=True, data=text))
    capture = Mock(side_effect=AssertionError("A screen read started a process"))
    monkeypatch.setattr(remote, "raw", raw)
    monkeypatch.setattr(remote, "capture", capture)
    assert remote.read_text(WindowId("86"), ansi=True) == text
    expected = GetTextRcPayload(match="id:86", extent="screen", ansi=True)
    assert raw.call_args.args == ("get-text", expected)
    capture.assert_not_called()


@pytest.mark.parametrize("response", [
    None, False, KittyRcResponse(ok=False), KittyRcResponse(ok=True),
])
def test_screen_read_keeps_fallback(
    monkeypatch: pytest.MonkeyPatch, *, response: KittyRcResponse | bool | None,
) -> None:
    """Keep the existing command path when a direct reply is unavailable."""
    remote = KittyRemote()
    monkeypatch.setattr(remote, "raw", Mock(return_value=response))
    capture = Mock(return_value="Fallback screen")
    monkeypatch.setattr(remote, "capture", capture)
    assert remote.read_text(WindowId("86")) == "Fallback screen"
    capture.assert_called_once()
