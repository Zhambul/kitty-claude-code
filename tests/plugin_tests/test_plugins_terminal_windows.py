# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal adapter window ownership tests."""

from __future__ import annotations

from dataclasses import replace

from domain.ids import SessionId, WindowId
from terminal.adapter import TerminalAdapter
from terminal.models.values import ACTIVITY_PANE_TAG, SCOREBOARD_PANE_TAG, SESSION_WINDOW_TAG, WindowProcess
from tests.fake_terminal import FakeSessions, FakeTerminal, window
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.terminal_plugin_values import PRIMARY_SESSION


def test_terminal_adapter_reads_session_window() -> None:
    """Verify terminal adapter reads the session window from evidence and checks it lives."""
    terminal = FakeTerminal(
        windows=[
            window(fixture.WINDOW_ONE_ID, tags={SESSION_WINDOW_TAG: fixture.SESSION_ONE_ID}),
        ],
    )
    sessions = FakeSessions({fixture.SESSION_ONE_ID: fixture.WINDOW_ONE_ID, "session-two": "window-gone"})
    adapter = TerminalAdapter(terminal.plugin(), sessions)

    assert adapter.window_for_session(PRIMARY_SESSION) == fixture.WINDOW_ONE_ID
    # the row outlived its window: a session id alone is not liveness
    assert adapter.window_for_session(SessionId("session-two")) is None
    assert adapter.window_for_session(SessionId("session-missing")) is None


def test_terminal_adapter_does_not_give_untagged() -> None:
    """Verify terminal adapter does not give an untagged window to a session."""
    terminal = FakeTerminal(windows=[window(fixture.WINDOW_ONE_ID)])
    adapter = TerminalAdapter(
        terminal.plugin(),
        FakeSessions({fixture.SESSION_ONE_ID: fixture.WINDOW_ONE_ID}),
    )

    assert adapter.window_for_session(PRIMARY_SESSION) is None
    assert adapter.live_sessions((PRIMARY_SESSION,)) == frozenset()


def test_terminal_adapter_rejects_copied_window() -> None:
    """Verify terminal adapter rejects a copied window from another foreground process."""
    terminal = FakeTerminal(
        windows=[
            replace(
                window(fixture.WINDOW_ONE_ID),
                processes=(WindowProcess(fixture.WINDOW_PROCESS_ID, ("/opt/codex", "resume")),),
            ),
        ],
    )
    adapter = TerminalAdapter(terminal.plugin(), FakeSessions())

    assert (
        adapter.window_hosts_process(
            WindowId(fixture.WINDOW_ONE_ID),
            fixture.DIFFERENT_WINDOW_PROCESS_ID,
            fixture.CLAUDE,
        )
        is False
    )
    assert (
        adapter.window_hosts_process(
            WindowId(fixture.WINDOW_ONE_ID),
            fixture.WINDOW_PROCESS_ID,
            fixture.CODEX_HARNESS,
        )
        is True
    )


def test_terminal_adapter_checks_liveness_against() -> None:
    """Verify terminal adapter checks liveness against a given window snapshot."""
    terminal = FakeTerminal(
        windows=[
            window(
                fixture.WINDOW_ONE_ID,
                tags={SESSION_WINDOW_TAG: fixture.SESSION_ONE_ID},
            ),
        ],
    )
    adapter = TerminalAdapter(
        terminal.plugin(),
        FakeSessions({fixture.SESSION_ONE_ID: fixture.WINDOW_ONE_ID}),
    )
    snapshot = terminal.windows()
    terminal.windows_on_screen.clear()

    assert adapter.window_is_live(
        SessionId(fixture.SESSION_ONE_ID),
        WindowId(fixture.WINDOW_ONE_ID),
        snapshot,
    )
    assert not adapter.window_is_live(
        SessionId("session-two"),
        WindowId(fixture.WINDOW_ONE_ID),
        snapshot,
    )


def test_terminal_adapter_gives_shared_window() -> None:
    """Verify terminal adapter gives a shared window to its new session owner."""
    terminal = FakeTerminal(
        windows=[
            window(fixture.WINDOW_ONE_ID, tags={SESSION_WINDOW_TAG: fixture.SESSION_NEW_ID}),
        ],
    )
    sessions = FakeSessions(
        {
            "session-old": fixture.WINDOW_ONE_ID,
            fixture.SESSION_NEW_ID: fixture.WINDOW_ONE_ID,
        },
    )
    adapter = TerminalAdapter(terminal.plugin(), sessions)

    assert adapter.window_for_session(SessionId("session-old")) is None
    assert adapter.window_for_session(SessionId(fixture.SESSION_NEW_ID)) == fixture.WINDOW_ONE_ID
    assert adapter.live_sessions(
        (
            SessionId("session-old"),
            SessionId(fixture.SESSION_NEW_ID),
        ),
    ) == frozenset((SessionId(fixture.SESSION_NEW_ID),))


def test_terminal_adapter_measures_activity_pane() -> None:
    """Verify terminal adapter measures the activity pane against its row."""
    terminal = FakeTerminal(
        windows=[
            window(fixture.WINDOW_ONE_ID, columns=fixture.HOST_PANE_WIDTH_PERCENT),
            window(
                fixture.WINDOW_TWO_ID,
                tags={ACTIVITY_PANE_TAG: fixture.SESSION_ONE_ID},
                columns=fixture.PANE_WIDTH_PERCENT,
                is_first_in_tab=False,
            ),
            # stacked INSIDE the activity pane's column — counting it would count
            # that column twice
            window(
                "window-three",
                tags={SCOREBOARD_PANE_TAG: fixture.SESSION_ONE_ID},
                columns=fixture.PANE_WIDTH_PERCENT,
                lines=5,
                is_first_in_tab=False,
            ),
        ],
    )
    adapter = TerminalAdapter(terminal.plugin(), FakeSessions())

    assert adapter.activity_pane_geometry(SessionId(fixture.SESSION_ONE_ID)) == (fixture.PANE_WIDTH_PERCENT, 100)

    adapter.set_activity_pane_width(SessionId(fixture.SESSION_ONE_ID), fixture.TARGET_PANE_WIDTH_PERCENT)
    assert terminal.resized == [(fixture.WINDOW_TWO_ID, "horizontal", 15)]
