# Copyright (c) 2026 Zhambyl Yermagambet
"""Reusable status predicates for E2E waits."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models.entry import MessageBodyResponse, TurnStartedBodyResponse

if TYPE_CHECKING:
    from domain.actor_state import ActorStatus
    from sdk.client import BaqylauClient, SessionRef
    from tests.e2e.testkit.references import Sessions


class StopFeedbackCheck:
    """Check that Stop hook feedback starts a turn."""

    def __init__(self, client: BaqylauClient, session: SessionRef) -> None:
        """Initialize the predicate."""
        self._client = client
        self._session = session

    def __call__(self) -> bool | None:
        """Return success when one feedback turn starts.

        Returns:
            Success when one feedback turn starts.

        """
        snapshot = self._client.sessions.snapshot(self._session)
        feedback = [
            entry
            for entry in snapshot.entries
            if isinstance(entry.body, MessageBodyResponse)
            and entry.body.role == "system"
            and entry.body.phase == "synthetic"
            and entry.body.content.text.startswith("Stop hook feedback:")
        ]
        if not feedback:
            return None
        feedback_turn = feedback[-1].turn_id
        starts = [
            entry
            for entry in snapshot.entries
            if isinstance(entry.body, TurnStartedBodyResponse) and entry.turn_id == feedback_turn
        ]
        return True if feedback_turn is not None and len(starts) == 1 else None


def lead_has_status(
    client: BaqylauClient,
    sessions: Sessions,
    name: str,
    expected: ActorStatus,
) -> bool:
    """Return whether the session lead has the expected status.

    Returns:
        Whether the session lead has the expected status.

    """
    snapshot = client.sessions.snapshot(sessions.get(name))
    return snapshot.lead().status == expected
