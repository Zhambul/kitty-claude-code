# Copyright (c) 2026 Zhambyl Yermagambet
"""Check child actor state in session snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit import assignment_states

if TYPE_CHECKING:
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.references import ActorRef


def actor_has_state(snapshot: SessionSnapshot, reference: ActorRef, state: str) -> bool | None:
    """Return true when an actor has the required state.

    Returns:
        True for the required state, else None.

    """
    return True if assignment_states.actor(snapshot, reference).state == state else None


def has_count(snapshot: SessionSnapshot, count: int, session_name: str) -> bool | None:
    """Return true when a session has the required child actor count.

    Returns:
        True for the required count, else None.

    Raises:
        AssertionError: If the session has more child actors than required.

    """
    actors = [actor for actor in snapshot.session_data.actors if actor.parent_actor_id is not None]
    if len(actors) > count:
        message = f"session {session_name!r} has {len(actors)} subagents"
        raise AssertionError(message)
    return True if len(actors) == count else None


def all_have_state(snapshot: SessionSnapshot, state: str) -> bool | None:
    """Return true when all child actors have the required state.

    Returns:
        True for the required state, else None.

    """
    actors = [actor for actor in snapshot.session_data.actors if actor.parent_actor_id is not None]
    if not actors:
        return None
    return True if all(actor.state == state for actor in actors) else None
