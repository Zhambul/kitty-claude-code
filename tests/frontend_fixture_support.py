# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared types for the frontend fixture server."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypedDict, Unpack

from core.git_status import RepositoryStatus
from core.repository import RepositoryQueries

if TYPE_CHECKING:
    from domain import event_base, ids as domain_ids, references


class FixtureEventArguments(TypedDict, total=False):
    """Optional canonical event identity fields."""

    session_id: domain_ids.SessionId | None
    actor_id: domain_ids.ActorId | None
    parent_actor_id: domain_ids.ActorId | None
    turn_id: domain_ids.TurnId | None
    seconds_ago: float


class FixtureEventSink(Protocol):
    """Accept canonical fixture events."""

    def add(
        self,
        name: str,
        payload: event_base.EventPayload,
        **arguments: Unpack[FixtureEventArguments],
    ) -> None:
        """Add one fixture event."""


class FixturePhaseContext(Protocol):
    """Declare state shared by fixture fact phases."""

    _events: FixtureEventSink
    _working_directory: str
    _model: references.ModelReference
    _account: references.AccountReference
    _turn: domain_ids.TurnId
    _active_lead: domain_ids.ActorId
    _child_actor: domain_ids.ActorId
    _waiting_session: domain_ids.SessionId
    _waiting_lead: domain_ids.ActorId
    _waiting_child: domain_ids.ActorId
    _parked_session: domain_ids.SessionId
    _parked_lead: domain_ids.ActorId


class FixtureRepositoryQueries(RepositoryQueries):
    """Keep the browser fixture independent of the source checkout."""

    @classmethod
    def status(cls, _working_directory: str) -> RepositoryStatus | None:
        """Return deterministic repository state.

        Returns:
            Deterministic repository state.

        """
        return RepositoryStatus(branch="main", worktree=None, dirty=False)
