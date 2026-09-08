# Copyright (c) 2026 Zhambyl Yermagambet
"""Resolve assignment actor and result values."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models import entry as entry_models

if TYPE_CHECKING:
    from api.sessiondata.models.actor import ActorResponse
    from sdk.state_models import AssignmentState


def actor_id(assignment: AssignmentState, actors: tuple[ActorResponse, ...]) -> str | None:
    """Return the actor that matches one assignment.

    Returns:
        The actor that matches one assignment.

    """
    can_match = assignment.actor_id in {None, assignment.owner_actor_id} and assignment.assigned_actor_name
    if can_match:
        candidates = [
            actor
            for actor in actors
            if actor.parent_actor_id == assignment.owner_actor_id and actor.name == assignment.assigned_actor_name
        ]
        if len(candidates) == 1:
            return candidates[0].actor_id
    return assignment.actor_id


def result(assignment: AssignmentState, entries: tuple[entry_models.EntryResponse, ...]) -> str | None:
    """Return the final message for one completed assignment.

    Returns:
        The final message for one completed assignment.

    """
    if assignment.state is None or assignment.result or assignment.actor_id is None:
        return None
    final_messages = [entry for entry in entries if _is_result(entry, assignment)]
    if final_messages:
        final_body = final_messages[-1].body
        if isinstance(final_body, entry_models.MessageBodyResponse):
            return final_body.content.text.strip()
    return None


def _is_result(entry: entry_models.EntryResponse, assignment: AssignmentState) -> bool:
    if entry.cursor <= assignment.started_cursor:
        return False
    if assignment.finished_cursor is not None and entry.cursor >= assignment.finished_cursor:
        return False
    if entry.actor_id != assignment.actor_id or not isinstance(entry.body, entry_models.MessageBodyResponse):
        return False
    return (
        entry.body.recipient_actor_id == assignment.owner_actor_id
        and entry.body.role in {"assistant", "peer"}
        and bool(entry.body.content.text.strip())
    )
