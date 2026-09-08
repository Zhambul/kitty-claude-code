# Copyright (c) 2026 Zhambyl Yermagambet
"""Pane command service tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.ids import SessionId, WindowId
from terminal.panes import commands as pane_commands
from tests.plugin_tests import support_audit, support_terminal, vocabulary as fixture
from tests.plugin_tests.pane_command_models import PaneAuditRecorder, PaneAuditRow, RecordingPaneTerminal
from tests.plugin_tests.terminal_plugin_values import PANE_WINDOW, PRIMARY_SESSION

if TYPE_CHECKING:
    from collections.abc import Callable

    from terminal.adapter import SessionTerminalResult


def test_pane_command_service_executes_gestures() -> None:
    """Verify pane command service executes gestures for the windows session."""
    terminal = RecordingPaneTerminal()
    remembered: list[tuple[str, int]] = []
    service = pane_commands.PaneCommandService(
        terminal, support_terminal.Widths(remembered), support_audit.silent_audit(),
    )

    outcomes = [
        service.toggle(PANE_WINDOW, fixture.PROJECT_PATH),
        service.grow(PANE_WINDOW, fixture.PROJECT_PATH),
        service.shrink(PANE_WINDOW, fixture.PROJECT_PATH),
        service.reset(PANE_WINDOW, fixture.PROJECT_PATH),
        service.set_percent(PANE_WINDOW, fixture.PROJECT_PATH, fixture.HOST_PANE_WIDTH_PERCENT),
    ]

    assert all(outcome.handled and outcome.succeeded for outcome in outcomes)
    assert terminal.toggles == [(PRIMARY_SESSION, fixture.PANE_DEFAULT_WIDTH_PERCENT)]
    assert terminal.resizes == [
        (PRIMARY_SESSION, 7),
        (PRIMARY_SESSION, -7),
    ]
    assert terminal.widths == [
        (PRIMARY_SESSION, fixture.PANE_DEFAULT_WIDTH_PERCENT),
        (PRIMARY_SESSION, fixture.HOST_PANE_WIDTH_PERCENT),
    ]
    assert remembered == [
        (fixture.PROJECT_PATH, fixture.PANE_WIDTH_PERCENT),
        (fixture.PROJECT_PATH, fixture.PANE_WIDTH_PERCENT),
        (fixture.PROJECT_PATH, fixture.PANE_DEFAULT_WIDTH_PERCENT),
        (fixture.PROJECT_PATH, fixture.HOST_PANE_WIDTH_PERCENT),
    ]


class _UnexpectedPaneTerminal:
    """Reject pane operations for a window without a session."""

    def session_for_window(self, window_id: WindowId | None) -> None:
        """Return no session for the window."""
        self.last_window_id = window_id

    def toggle_session_panes(self, session_id: SessionId, width_percent: int) -> SessionTerminalResult:
        """Reject an unexpected pane toggle.

        Raises:
            AssertionError: For every toggle request.

        """
        raise AssertionError((session_id, width_percent))

    def resize_activity_pane(self, session_id: SessionId, columns: int) -> SessionTerminalResult:
        """Reject an unexpected pane resize.

        Raises:
            AssertionError: For every resize request.

        """
        raise AssertionError((session_id, columns))

    def activity_pane_geometry(self, session_id: SessionId) -> tuple[int, int] | None:
        """Reject an unexpected pane geometry read.

        Raises:
            AssertionError: For every geometry request.

        """
        raise AssertionError(session_id)

    def set_activity_pane_width(
        self,
        session_id: SessionId,
        width_percent: int,
    ) -> SessionTerminalResult:
        """Reject an unexpected pane width write.

        Raises:
            AssertionError: For every width request.

        """
        raise AssertionError((session_id, width_percent))


def test_pane_command_in_tab_without_session() -> None:
    """Verify pane command in a tab without a session is quietly unhandled."""
    outcome = pane_commands.PaneCommandService(
        _UnexpectedPaneTerminal(), support_terminal.Widths([]), support_audit.silent_audit(),
    ).toggle(
        WindowId(""),
        fixture.PROJECT_PATH,
    )
    assert outcome == pane_commands.PaneCommandOutcome(handled=False, succeeded=True)


def test_every_pane_command_method_writes_exactly() -> None:
    """Verify every pane command method writes exactly one audit row through one core."""
    rows: list[PaneAuditRow] = []
    service = pane_commands.PaneCommandService(
        RecordingPaneTerminal(),
        support_terminal.Widths([]),
        PaneAuditRecorder(rows),
    )
    calls: tuple[Callable[[], pane_commands.PaneCommandOutcome], ...] = (
        lambda: service.toggle(PANE_WINDOW, fixture.PROJECT_PATH),
        lambda: service.grow(PANE_WINDOW, fixture.PROJECT_PATH),
        lambda: service.shrink(PANE_WINDOW, fixture.PROJECT_PATH),
        lambda: service.reset(PANE_WINDOW, fixture.PROJECT_PATH),
        lambda: service.set_percent(PANE_WINDOW, fixture.PROJECT_PATH, fixture.HOST_PANE_WIDTH_PERCENT),
    )

    for expected_count, call in enumerate(calls, start=1):
        call()
        _assert_pane_audit(rows, expected_count)


def _assert_pane_audit(rows: list[PaneAuditRow], expected_count: int) -> None:
    assert len(rows) == expected_count
    action, content = rows[-1]
    assert action == "pane-command"
    assert isinstance(content, pane_commands.PaneCommandAudit)
    assert content.ok is True
