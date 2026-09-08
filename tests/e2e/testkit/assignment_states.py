# Copyright (c) 2026 Zhambyl Yermagambet
"""Read typed assignment state from a session snapshot."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit.references import ActorRef

if TYPE_CHECKING:
    from api.sessiondata.models.actor import ActorResponse
    from sdk.state import AssignmentState, SessionSnapshot
    from tests.e2e.testkit.references import AssignmentRef


def assignment(snapshot: SessionSnapshot, reference: AssignmentRef) -> AssignmentState:
    """Return state for one assignment reference.

    Returns:
        The matching assignment state.

    Raises:
        AssertionError: If the snapshot does not have one matching assignment.

    """
    found = [
        assignment_state
        for assignment_state in snapshot.assignments()
        if assignment_state.assignment_id == reference.assignment_id
    ]
    if len(found) != 1:
        message = f"assignment {reference.assignment_id!r} has {len(found)} matches"
        raise AssertionError(message)
    return found[0]


def has_state(snapshot: SessionSnapshot, reference: AssignmentRef, state: str) -> bool | None:
    """Return true when an assignment has the required state.

    Returns:
        True for the required state, else None.

    """
    return True if assignment(snapshot, reference).state == state else None


def result_contains(snapshot: SessionSnapshot, reference: AssignmentRef, text: str) -> bool | None:
    """Return true when an assignment result contains text.

    Returns:
        True when the result contains text, else None.

    """
    return True if text in assignment(snapshot, reference).result else None


def actor(snapshot: SessionSnapshot, reference: ActorRef) -> ActorResponse:
    """Return the actor for one actor reference.

    Returns:
        The matching actor.

    """
    return snapshot.actor(reference.actor_id)


def assigned_actor(
    snapshot: SessionSnapshot,
    reference: AssignmentRef,
) -> ActorRef | None:
    """Return the actor assigned to one assignment.

    Returns:
        The assigned child actor, or ``None`` before the assignment has one.

    """
    actor_id = assignment(snapshot, reference).actor_id
    if actor_id is None:
        return None
    assigned = snapshot.actor(actor_id)
    if assigned.parent_actor_id is None:
        return None
    return ActorRef(reference.session, actor_id)
