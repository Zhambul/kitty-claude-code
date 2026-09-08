# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata paint support."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests import (
    canonical_sessiondata_components as sessiondata_components,
    canonical_sessiondata_values as session_values,
)

if TYPE_CHECKING:
    from tests.canonical_sessiondata_components import domain as session_domain


class RecordingTabs:
    """Represent recording tabs."""

    def __init__(self) -> None:
        """Create empty terminal tab records."""
        self.painted: list[tuple[str, sessiondata_components.terminal.terminal_value_models.RGB | None]] = []
        self.sessions: list[session_domain.ids.SessionId] = []

    def paint_session_tab(
        self,
        session_id: session_domain.ids.SessionId,
        appearance: sessiondata_components.terminal.terminal_value_models.TabAppearance,
    ) -> sessiondata_components.terminal.adapter.SessionTerminalResult:
        """Record a tab color request.

        Returns:
            A successful terminal result.

        """
        self.sessions.append(session_id)
        self.painted.append((session_values.PAINT_TOOL_NAME, appearance.active_background))
        return sessiondata_components.terminal.adapter.SessionTerminalResult(succeeded=True)

    def clear_session_tab(
        self, session_id: session_domain.ids.SessionId,
    ) -> sessiondata_components.terminal.adapter.SessionTerminalResult:
        """Record a tab color reset.

        Returns:
            A successful terminal result.

        """
        self.sessions.append(session_id)
        self.painted.append(("clear", None))
        return sessiondata_components.terminal.adapter.SessionTerminalResult(succeeded=True)


class FixedSessions:
    """Represent fixed sessions."""

    def __init__(self, lead_actor_id: session_domain.ids.ActorId) -> None:
        """Store the lead actor fixture."""
        self.lead_actor_id = lead_actor_id

    def find(self, session_id: session_domain.ids.SessionId) -> sessiondata_components.harness.session.Session | None:
        """Return find.

        Returns:
            Find.

        """
        if session_id != session_values.SESSION:
            return None
        return sessiondata_components.harness.session.Session(
            session_values.SESSION, self.lead_actor_id, "fixture", session_values.WORKING_DIRECTORY,
        )


def paint_actions(recording_tabs: RecordingTabs) -> list[str]:
    """Read the recorded tab actions.

    Returns:
        The action names in recorded order.

    """
    return [action for action, _colour in recording_tabs.painted]
