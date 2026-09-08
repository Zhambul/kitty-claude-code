# Copyright (c) 2026 Zhambyl Yermagambet
"""Server-side execution of the terminal pane keybinding gestures.

The keybinding process is a thin HTTP client (`terminal/panes/client.py`): it can
only observe its own environment — the terminal window the keypress landed in
and the working directory — and ships both here. Everything the gesture *does*
(session lookup, pane control, remembered widths) runs in the daemon, on the
one application graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol

from audit.documents import AuditDocument
from domain.ids import SessionId, WindowId

if TYPE_CHECKING:
    from collections.abc import Callable

    from terminal.panes import contracts


class PaneCommand(StrEnum):
    """Represent pane command."""

    TOGGLE = "toggle"
    GROW = "grow"
    SHRINK = "shrink"
    RESET = "reset"
    SETPCT = "setpct"


@dataclass(frozen=True)
class PaneCommandOutcome:
    """Represent pane command outcome."""

    handled: bool
    succeeded: bool
    reason: str | None = None


class PaneCommandAudit(AuditDocument):
    """Represent pane command audit."""

    command: PaneCommand
    window_id: WindowId
    session_id: SessionId
    ok: bool
    why: str


class _PaneCommandContext(Protocol):
    """Provide dependencies for pane command execution."""

    _terminal: contracts.PaneTerminal
    _widths: contracts.PaneWidths
    _audit: contracts.PaneAudit

    def _remember_current_width(self, session_id: SessionId, working_directory: str) -> None:
        """Remember the current activity-pane width."""


class PaneCommandExecution:
    """Provide internal pane command execution."""

    def _audited(
        self: _PaneCommandContext,
        pane_command: PaneCommand,
        window_id: WindowId | None,
        working_directory: str,
        gesture: Callable[[SessionId], PaneCommandOutcome],
    ) -> PaneCommandOutcome:
        if not working_directory:
            msg = "working_directory is required"
            raise ValueError(msg)
        session_id = self._terminal.session_for_window(window_id)
        outcome = (
            PaneCommandOutcome(handled=False, succeeded=True)
            if session_id is None
            else gesture(session_id)
        )
        self._audit.state_file(
            "",
            working_directory,
            "pane-command",
            PaneCommandAudit(
                command=pane_command,
                window_id=window_id or WindowId(""),
                session_id=session_id or SessionId(""),
                ok=outcome.succeeded,
                why=outcome.reason or "",
            ),
        )
        return outcome

    def _toggle(self: _PaneCommandContext, session_id: SessionId, working_directory: str) -> PaneCommandOutcome:
        result = self._terminal.toggle_session_panes(session_id, self._widths.width_percent(working_directory))
        return PaneCommandOutcome(handled=True, succeeded=result.succeeded, reason=result.reason)

    def _resize(
        self: _PaneCommandContext,
        session_id: SessionId,
        working_directory: str,
        columns: int | None,
        *,
        grow: bool,
    ) -> PaneCommandOutcome:
        step = self._widths.resize_columns() if columns is None else columns
        if step <= 0:
            msg = "pane resize columns must be positive"
            raise ValueError(msg)
        result = self._terminal.resize_activity_pane(session_id, step if grow else -step)
        if result.succeeded:
            self._remember_current_width(session_id, working_directory)
        return PaneCommandOutcome(handled=True, succeeded=result.succeeded, reason=result.reason)

    def _set_width(
        self: _PaneCommandContext,
        session_id: SessionId,
        working_directory: str,
        width_percent: int,
    ) -> PaneCommandOutcome:
        result = self._terminal.set_activity_pane_width(session_id, width_percent)
        if result.succeeded:
            self._widths.remember_width(working_directory, width_percent)
        return PaneCommandOutcome(handled=True, succeeded=result.succeeded, reason=result.reason)

    def _remember_current_width(self: _PaneCommandContext, session_id: SessionId, working_directory: str) -> None:
        geometry = self._terminal.activity_pane_geometry(session_id)
        if geometry is None:
            return
        current_columns, total_columns = geometry
        if total_columns:
            self._widths.remember_width(working_directory, round(100 * current_columns / total_columns))


class PaneCommandService(PaneCommandExecution):
    """Represent pane command service."""

    def __init__(
        self,
        terminal_adapter: contracts.PaneTerminal,
        pane_width_service: contracts.PaneWidths,
        audit_recorder: contracts.PaneAudit,
    ) -> None:
        """Initialize the object."""
        self._terminal = terminal_adapter
        self._widths = pane_width_service
        self._audit = audit_recorder

    def toggle(self, window_id: WindowId | None, working_directory: str) -> PaneCommandOutcome:
        """Toggle.

        Returns:
            The pane command outcome.

        """
        return self._audited(
            PaneCommand.TOGGLE,
            window_id,
            working_directory,
            lambda session_id: self._toggle(session_id, working_directory),
        )

    def grow(
        self,
        window_id: WindowId | None,
        working_directory: str,
        columns: int | None = None,
    ) -> PaneCommandOutcome:
        """Grow.

        Returns:
            The pane command outcome.

        """
        return self._audited(
            PaneCommand.GROW,
            window_id,
            working_directory,
            lambda session_id: self._resize(session_id, working_directory, columns, grow=True),
        )

    def shrink(
        self,
        window_id: WindowId | None,
        working_directory: str,
        columns: int | None = None,
    ) -> PaneCommandOutcome:
        """Shrink.

        Returns:
            The pane command outcome.

        """
        return self._audited(
            PaneCommand.SHRINK,
            window_id,
            working_directory,
            lambda session_id: self._resize(session_id, working_directory, columns, grow=False),
        )

    def reset(self, window_id: WindowId | None, working_directory: str) -> PaneCommandOutcome:
        """Reset.

        Returns:
            The pane command outcome.

        """
        return self._audited(
            PaneCommand.RESET,
            window_id,
            working_directory,
            lambda session_id: self._set_width(
                session_id,
                working_directory,
                self._widths.configured_width_percent(),
            ),
        )

    def set_percent(self, window_id: WindowId | None, working_directory: str, percent: int) -> PaneCommandOutcome:
        """Set percent.

        Returns:
            The pane command outcome.

        """
        return self._audited(
            PaneCommand.SETPCT,
            window_id,
            working_directory,
            lambda session_id: self._set_width(session_id, working_directory, percent),
        )
