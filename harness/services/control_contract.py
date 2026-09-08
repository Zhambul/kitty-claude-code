# Copyright (c) 2026 Zhambyl Yermagambet
"""Define the ports for confirmed control effects."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from domain.entries import SessionEntry
    from domain.ids import SessionId
    from harness.models.controls import (
        CloseSession,
        DecidePlan,
        RenameSession,
        SelectEffort,
        SelectModel,
        SendText,
    )
    from harness.models.session import (
        Session,
    )
    from harness.services.open_session_work import SessionCloseWork


class InterruptMarker(Protocol):
    """Mark an interrupt that needs a fallback fact."""

    def mark(self, session_id: SessionId) -> None:
        """Mark a session interrupt."""
        ...


class ControlEffects(Protocol):
    """Record confirmed effects of controls."""

    def work_before_close(self, session_id: SessionId) -> tuple[SessionCloseWork, ...]:
        """Return open work before a session closes."""
        ...

    def message_queued(self, session: Session, send_text: SendText) -> None:
        """Record a queued message."""
        ...

    def session_closed(
        self,
        session: Session,
        close_session: CloseSession,
        observations: tuple[SessionCloseWork, ...],
    ) -> None:
        """Record a closed session."""
        ...

    def session_renamed(self, session: Session, rename_session: RenameSession) -> None:
        """Record a renamed session."""
        ...

    def selection_changed(self, session: Session, selection: SelectModel | SelectEffort) -> None:
        """Record a changed model or effort."""
        ...

    def plan_decided(
        self,
        session: Session,
        decide_plan: DecidePlan,
        pending_session_entry: SessionEntry,
    ) -> None:
        """Record a plan decision."""
        ...
