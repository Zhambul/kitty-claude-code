# Copyright (c) 2026 Zhambyl Yermagambet
"""One session rename operation for controls and observed title facts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.event_session import SessionTitleChanged
from harness.contract import CanonicalEventReaction
from harness.models.controls import (
    ControlAcknowledgement,
    ControlContext,
    ControlResult,
    MessageDeliveryResult,
    RenameSession,
)
from naming.errors import InvalidRenameResultError, TerminalRenameError

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.contract import HarnessController
    from terminal.adapter import TerminalAdapter


class SessionRenamer(CanonicalEventReaction):
    """Apply a harness rename and keep its live terminal tab in agreement.

    A control uses `rename` because it knows the requested title. A native or
    automatic title source uses the same tab operation through `react`.
    """

    def __init__(self, terminal_adapter: TerminalAdapter) -> None:
        """Create a renamer with the terminal adapter."""
        self._terminal = terminal_adapter

    def rename(
        self,
        controller: HarnessController,
        rename_session: RenameSession,
        control_context: ControlContext,
    ) -> ControlResult:
        """Apply a rename through the harness and terminal.

        Returns:
            The control result.

        Raises:
            InvalidRenameResultError: If a rename result is not valid.

        """
        outcome = controller.execute(rename_session, control_context)
        if isinstance(outcome, MessageDeliveryResult):
            raise InvalidRenameResultError
        if outcome.status != ControlAcknowledgement.ACKNOWLEDGED:
            return outcome
        terminal_outcome = self._terminal.rename_session_tab(
            rename_session.session_id,
            rename_session.name,
        )
        if terminal_outcome.succeeded:
            return outcome
        return ControlResult(
            rename_session.request_id,
            ControlAcknowledgement.INDETERMINATE,
            terminal_outcome.reason or "terminal title was not changed",
        )

    def react(self, canonical_event: CanonicalEvent[EventPayload]) -> None:
        """Apply an observed session title to the terminal tab.

        Raises:
            TerminalRenameError: If a terminal rename fails.

        """
        payload = canonical_event.payload
        if not isinstance(payload, SessionTitleChanged):
            return
        outcome = self._terminal.rename_session_tab(
            canonical_event.session_id,
            payload.title,
        )
        if not outcome.succeeded:
            raise TerminalRenameError(outcome.reason)
