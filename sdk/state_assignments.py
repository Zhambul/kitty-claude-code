# Copyright (c) 2026 Zhambyl Yermagambet
"""Materialize assignment state from session entries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models import entry as entry_models
from sdk.state_models import AssignmentState

if TYPE_CHECKING:
    from typing import TypeGuard


def assignments(entries: tuple[entry_models.EntryResponse, ...]) -> tuple[AssignmentState, ...]:
    """Return materialized assignments.

    Returns:
        Materialized assignments.

    """
    folded: dict[str, AssignmentState] = {}
    for entry in entries:
        _fold_entry(folded, entry)
    return tuple(folded.values())


def _fold_entry(folded: dict[str, AssignmentState], entry: entry_models.EntryResponse) -> None:
    body = entry.body
    if isinstance(body, entry_models.AssignmentStartedBodyResponse):
        folded[body.assignment_id] = _started(entry, body)
    elif isinstance(body, entry_models.AssignmentFinishedBodyResponse):
        _finish(folded, entry, body)
    elif _is_prompt(body, entry):
        _attach(folded, entry, body)


def _is_prompt(
    body: entry_models.EntryBodyResponse,
    entry: entry_models.EntryResponse,
) -> TypeGuard[entry_models.MessageBodyResponse]:
    return (
        isinstance(body, entry_models.MessageBodyResponse)
        and body.role == "parent"
        and body.phase == "prompt"
        and entry.parent_actor_id is not None
    )


def _started(
    entry: entry_models.EntryResponse,
    body: entry_models.AssignmentStartedBodyResponse,
) -> AssignmentState:
    return AssignmentState(
        assignment_id=body.assignment_id,
        owner_actor_id=entry.parent_actor_id or entry.actor_id,
        actor_id=None if entry.parent_actor_id is None else entry.actor_id,
        turn_id=entry.turn_id,
        assigned_actor_name=body.assigned_actor_name,
        requested_prompt=None if body.prompt is None else body.prompt.text,
        started_cursor=entry.cursor,
    )


def _attach(
    folded: dict[str, AssignmentState],
    entry: entry_models.EntryResponse,
    body: entry_models.MessageBodyResponse,
) -> None:
    candidates = [assignment for assignment in folded.values() if _matches_unbound(assignment, entry, body)]
    if len(candidates) == 1:
        candidates[0].actor_id = entry.actor_id


def _matches_unbound(
    assignment: AssignmentState,
    entry: entry_models.EntryResponse,
    body: entry_models.MessageBodyResponse,
) -> bool:
    if assignment.actor_id is not None or assignment.state is not None:
        return False
    if assignment.owner_actor_id != entry.parent_actor_id or assignment.started_cursor >= entry.cursor:
        return False
    requested_prompt = assignment.requested_prompt
    return requested_prompt is not None and requested_prompt.strip() == body.content.text.strip()


def _finish(
    folded: dict[str, AssignmentState],
    entry: entry_models.EntryResponse,
    body: entry_models.AssignmentFinishedBodyResponse,
) -> None:
    assignment = folded.get(body.assignment_id)
    if assignment is None:
        assignment = AssignmentState(
            assignment_id=body.assignment_id,
            owner_actor_id=entry.parent_actor_id or entry.actor_id,
            actor_id=entry.actor_id,
            turn_id=entry.turn_id,
            assigned_actor_name=None,
            requested_prompt=None,
            started_cursor=entry.cursor,
        )
        folded[body.assignment_id] = assignment
    else:
        assignment.actor_id = entry.actor_id
    assignment.state = body.state
    assignment.result = "" if body.result is None else body.result.text
    assignment.finished_cursor = entry.cursor
