# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify PTY text and key input behavior."""

from __future__ import annotations

import time
from contextlib import nullcontext
from functools import partial
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

from terminal.impl.pty import plugin as pty_module
from terminal.models import input as terminal_input
from terminal.models.values import WindowId
from tests import terminal_pty_fixture as pty_fixture, terminal_pty_input_support as input_support

if TYPE_CHECKING:
    from terminal.impl.pty.registry import PtyWindows

pytest_plugins = ("tests.terminal_pty_fixture",)


def test_typing_and_keying_reach_the_program(terminal: pty_fixture.PtyFixture) -> None:
    """Verify typed text and keys reach the PTY program."""
    plugin, _ = terminal
    window_id = pty_fixture.open_terminal(terminal, pty_fixture.CAT_COMMAND)
    assert plugin.input.submit_text(
        terminal_input.TextSubmitRequest(window_id, "typed line", terminal_input.TextInputMode.TYPE),
    ).succeeded
    pty_fixture.await_screen(plugin, window_id, "typed line")
    assert plugin.input.submit_text(
        terminal_input.TextSubmitRequest(window_id, "pasted line", terminal_input.TextInputMode.PASTE),
    ).succeeded
    pty_fixture.await_screen(plugin, window_id, "pasted line")
    assert plugin.input.send_key(terminal_input.KeySendRequest(window_id, "ctrl+d")).succeeded
    deadline = time.monotonic() + pty_fixture.TIMEOUT_SECONDS
    while plugin.metadata.windows() and time.monotonic() < deadline:
        time.sleep(pty_fixture.POLL_SECONDS)
    assert not plugin.metadata.windows(), "cat outlived the ctrl+d that should have ended it"


def test_text_submit_keeps_enter_in_separate() -> None:
    """Verify text submit writes Enter after the payload paint wait."""
    events: list[input_support.TerminalInputEvent] = []
    window = SimpleNamespace(
        revision=7,
        write=partial(input_support.record_terminal_write, events),
        wait_for_screen_change=partial(input_support.record_screen_wait, events),
    )
    windows = SimpleNamespace(get=lambda _window_id: window, lock=nullcontext())
    result = pty_module.PtyInput(cast("PtyWindows", windows)).submit_text(
        terminal_input.TextSubmitRequest(WindowId("window-one"), "queued prompt", terminal_input.TextInputMode.PASTE),
    )
    assert result.succeeded
    assert events == [
        ("write", b"\x1b[200~queued prompt\x1b[201~"),
        ("paint", 7, pty_module.SUBMIT_PAINT_TIMEOUT_SECONDS),
        ("write", b"\r"),
    ]


def test_text_insert_never_writes_enter() -> None:
    """Verify text insert never writes an Enter byte."""
    events: list[bytes] = []
    window = SimpleNamespace(write=partial(input_support.record_inserted_payload, events))
    windows = SimpleNamespace(get=lambda _window_id: window, lock=nullcontext())
    result = pty_module.PtyInput(cast("PtyWindows", windows)).insert_text(
        terminal_input.TextInsertRequest(
            WindowId("window-one"),
            "saved draft",
            terminal_input.TextInputMode.PASTE,
        ),
    )
    assert result.succeeded
    assert events == [b"\x1b[200~saved draft\x1b[201~"]


def test_key_this_terminal_cannot_send_is_refused(terminal: pty_fixture.PtyFixture) -> None:
    """Verify unsupported keys are refused rather than guessed."""
    plugin, _ = terminal
    window_id = pty_fixture.open_terminal(terminal, pty_fixture.CAT_COMMAND)
    refused = plugin.input.send_key(terminal_input.KeySendRequest(window_id, "f13"))
    assert not refused.succeeded
    assert "f13" in (refused.reason or "")
