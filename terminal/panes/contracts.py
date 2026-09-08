# Copyright (c) 2026 Zhambyl Yermagambet
"""Contracts required by terminal pane commands."""

from typing import Protocol

from audit.documents import AuditContent
from domain.ids import SessionId, WindowId


class PaneResult(Protocol):
    """Provide fields that pane commands report."""

    @property
    def succeeded(self) -> bool:
        """Whether the command succeeded."""
        ...

    @property
    def reason(self) -> str | None:
        """The failure reason when one exists."""
        ...


class PaneTerminal(Protocol):
    """Provide session pane operations."""

    def session_for_window(self, window_id: WindowId | None) -> SessionId | None:
        """Find the session that owns a window."""
        ...

    def toggle_session_panes(self, session_id: SessionId, width_percent: int) -> PaneResult:
        """Toggle panes for one session."""
        ...

    def resize_activity_pane(self, session_id: SessionId, columns: int) -> PaneResult:
        """Resize the activity pane."""
        ...

    def set_activity_pane_width(self, session_id: SessionId, width_percent: int) -> PaneResult:
        """Set the activity pane width."""
        ...

    def activity_pane_geometry(self, session_id: SessionId) -> tuple[int, int] | None:
        """Return the activity pane geometry."""
        ...


class PaneWidths(Protocol):
    """Read and store pane width policy."""

    def width_percent(self, working_directory: str) -> int:
        """Return the stored width."""
        ...

    def configured_width_percent(self) -> int:
        """Return the configured width."""
        ...

    def resize_columns(self) -> int:
        """Return the resize step."""
        ...

    def remember_width(self, working_directory: str, width_percent: int) -> None:
        """Store a width."""
        ...


class PaneAudit(Protocol):
    """Record pane command audit documents."""

    def state_file(self, log: str, path: str, action: str, content: AuditContent = "") -> None:
        """Record one pane command."""
        ...
