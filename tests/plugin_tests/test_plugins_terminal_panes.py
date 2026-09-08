# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal adapter pane lifecycle tests."""

from __future__ import annotations

from pathlib import Path

from core.daemon.contract import HOST_ADDRESS, PORT_NUMBER
from terminal.adapter import SessionPaneRequest, TerminalAdapter
from terminal.models.values import ACTIVITY_PANE_TAG, SCOREBOARD_PANE_TAG, SESSION_WINDOW_TAG
from tests.fake_terminal import FakeSessions, FakeTerminal, window
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_terminal import pane_terminal
from tests.plugin_tests.terminal_plugin_values import PRIMARY_SESSION, PRIMARY_WINDOW

SCOREBOARD_LINE_COUNT = 5


def test_terminal_adapter_opens_canon_processes() -> None:
    """Verify terminal adapter opens canonical processes with generic tags."""
    terminal, adapter = pane_terminal()

    result = adapter.open_session_panes(
        SessionPaneRequest(PRIMARY_SESSION, PRIMARY_WINDOW, fixture.PANE_WIDTH_PERCENT),
    )

    assert result.succeeded
    _assert_terminal_pane_layout(terminal)
    # One client program, told where the daemon listens and which stream to open:
    # a pane imports nothing of ours, so everything it cannot observe is argv.
    pane_client = str(Path(__file__).parents[2] / "client" / "terminal_pane.py")
    assert [request.command[1:] for request in terminal.opened_panes] == [
        (pane_client, HOST_ADDRESS, str(PORT_NUMBER), fixture.SESSION_ONE_ID, "mirror"),
        (pane_client, HOST_ADDRESS, str(PORT_NUMBER), fixture.SESSION_ONE_ID, "scoreboard"),
    ]


def _assert_terminal_pane_layout(terminal: FakeTerminal) -> None:
    """Verify the generic tags, anchors, and focus of session panes."""
    assert terminal.tagged == [(fixture.WINDOW_ONE_ID, {SESSION_WINDOW_TAG: fixture.SESSION_ONE_ID})]
    assert [dict(request.tags) for request in terminal.opened_panes] == [
        {ACTIVITY_PANE_TAG: fixture.SESSION_ONE_ID},
        {SCOREBOARD_PANE_TAG: fixture.SESSION_ONE_ID},
    ]
    # The anchor is stated as intent, never as one terminal's match syntax.
    assert terminal.opened_panes[0].anchor.window_id == fixture.WINDOW_ONE_ID
    assert terminal.opened_panes[1].anchor.tag == (ACTIVITY_PANE_TAG, fixture.SESSION_ONE_ID)
    assert terminal.focused == [fixture.WINDOW_ONE_ID]


def test_pane_process_that_exits_on_startup() -> None:
    """A launch is not a pane until the pane is still there.

    Measured (session 11b25475, 2026-08-17): the pane processes died on their
    first import, every time. kitty had made the window, so `open_pane` reported
    success; the window vanished with the process, and the composite failed with
    "scoreboard pane is not open" — a symptom of the symptom. Now the reason names
    the thing that happened.
    """
    terminal = FakeTerminal(
        windows=[window(fixture.WINDOW_ONE_ID, tags={})],
        current_window=fixture.WINDOW_ONE_ID,
        pane_processes_die=True,
    )
    adapter = TerminalAdapter(terminal.plugin(), FakeSessions({fixture.SESSION_ONE_ID: fixture.WINDOW_ONE_ID}))

    result = adapter.open_session_panes(
        SessionPaneRequest(PRIMARY_SESSION, PRIMARY_WINDOW, fixture.PANE_WIDTH_PERCENT),
    )

    assert not result.succeeded
    assert result.reason == "mirror pane process exited on startup"


def test_terminal_adapter_settles_scoreboard() -> None:
    """Verify terminal adapter settles the scoreboard on its five rows."""
    terminal, adapter = pane_terminal()

    adapter.open_session_panes(SessionPaneRequest(PRIMARY_SESSION, PRIMARY_WINDOW, fixture.PANE_WIDTH_PERCENT))

    scoreboards = [found for found in terminal.windows() if found.tags.get(SCOREBOARD_PANE_TAG)]
    scoreboard = scoreboards[0]
    assert scoreboard.lines == SCOREBOARD_LINE_COUNT
    assert terminal.resized == [(scoreboard.window_id, "vertical", 2)]


def test_terminal_adapter_leaves_panes_it_finds() -> None:
    """Verify terminal adapter leaves panes it finds already open."""
    terminal, adapter = pane_terminal()
    adapter.open_session_panes(SessionPaneRequest(PRIMARY_SESSION, PRIMARY_WINDOW, fixture.PANE_WIDTH_PERCENT))
    terminal.opened_panes.clear()

    adapter.open_session_panes(SessionPaneRequest(PRIMARY_SESSION, PRIMARY_WINDOW, fixture.PANE_WIDTH_PERCENT))

    assert terminal.opened_panes == []


def test_terminal_adapter_close_removes_session() -> None:
    """Verify terminal adapter close removes the session window tag."""
    terminal, adapter = pane_terminal()
    adapter.open_session_panes(SessionPaneRequest(PRIMARY_SESSION, PRIMARY_WINDOW, fixture.PANE_WIDTH_PERCENT))
    terminal.tagged.clear()

    result = adapter.close_session_panes(PRIMARY_SESSION)

    assert result.succeeded
    assert terminal.tagged == [(fixture.WINDOW_ONE_ID, {SESSION_WINDOW_TAG: ""})]
    assert terminal.cleared == [fixture.WINDOW_ONE_ID]
    assert not any(found.tags.get(ACTIVITY_PANE_TAG) for found in terminal.windows())
