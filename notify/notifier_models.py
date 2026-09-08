# Copyright (c) 2026 Zhambyl Yermagambet
"""Notifications derived from canonical session state."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from domain.actor_state import ActorStatus
from domain.ids import SessionId
from notify.channels.alert import Alert
from notify.channels.retraction import NotificationHandle

if TYPE_CHECKING:
    from collections.abc import Mapping


# The two states worth interrupting you for. `awaiting_background` is DELIBERATELY
# not among them: a turn that ended while its own background job still runs has not
# finished producing what you would come back to read, and an alert then is early.
# Being unmapped is not a gap — the lookup returning None is how a state says "no
# alert", the same way `idle` and `working` do.
#
# It became reachable when background work stopped being ended by its own launch
# (engine/projections/tabstate.py), so its consequence is new: a session stays
# unalerted until the JOB reports its end, and one that never reports one stays
# unalerted for the rest of the session. The alert that DOES fire is the one for
# the next thing that asks you something.
NOTIFICATION_KINDS = MappingProxyType({
    "awaiting_attention": "asking",
    "awaiting_response": "done",
})


def attention_count(states: Mapping[SessionId, ActorStatus | None]) -> int:
    """Count sessions that need attention.

    Returns:
        The number of sessions in a notification state.

    """
    return sum(state in NOTIFICATION_KINDS for state in states.values())


@dataclass
class PendingNotification:
    """Represent pending notification."""

    session_id: SessionId
    state: ActorStatus
    kind: str
    project: str
    title: str
    due_at: float
    pushed: bool = False

    def payload(self) -> Alert:
        """Return the payload.

        Returns:
            Payload.

        """
        return Alert(
            session_id=self.session_id,
            state=self.state,
            kind=self.kind,
            project=self.project,
            title=self.title,
        )


@dataclass(frozen=True)
class Alertable:
    """Represent alertable.

    One attended session, as the notifier reads it: who it is, what it is
        called, and the one word that decides whether to interrupt you.
    """

    session_id: SessionId
    title: str
    project: str
    status: ActorStatus | None


@dataclass
class DeliveredNotification:
    """Represent delivered notification."""

    session_id: SessionId
    state: ActorStatus
    notification_handle: NotificationHandle
    delivered_at: float
