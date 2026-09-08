# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for terminal text input."""

from __future__ import annotations

from terminal.impl.kitty.plugin import kitty_plugin
from terminal.models.input import KeySendRequest, TextInputMode, TextInsertRequest
from terminal.models.values import WindowId
from tests.terminal_contract_remote import FakeRemote


def test_kitty_encodes_the_terminal_escape_key() -> None:
    """Verify kitty encodes the terminal escape key."""
    remote = FakeRemote()

    result = kitty_plugin(remote).input.send_key(KeySendRequest(WindowId("7"), "escape"))

    assert result.succeeded
    assert remote.calls == [("send-key", "--match", "id:7", "esc")]


def test_kitty_insert_does_not_submit_the_text() -> None:
    """Verify kitty insert does not submit the text."""
    remote = FakeRemote()
    plugin = kitty_plugin(remote)

    result = plugin.input.insert_text(TextInsertRequest(WindowId("7"), "saved draft", TextInputMode.PASTE))

    assert result.succeeded
    assert remote.calls == [("insert-text", "7", "saved draft", True)]
