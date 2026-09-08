# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable turns for actor assignments."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import MessageBodyResponse
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one

if TYPE_CHECKING:
    from api.sessiondata.models.entry import EntryResponse
    from sdk.client import SessionWatch
    from sdk.state import AssignmentState, SessionSnapshot

USER_MESSAGE_ROLE = "user"
PROMPT_MESSAGE_PHASE = "prompt"


def _matches_assignment_prompt(
    entry: EntryResponse,
    actor_reference: refs.ActorRef,
    assignment: AssignmentState,
    delivered_prompt: str,
) -> bool:
    if entry.cursor <= assignment.started_cursor or entry.actor_id != actor_reference.actor_id:
        return False
    if not isinstance(entry.body, MessageBodyResponse):
        return False
    return (
        entry.body.role in {USER_MESSAGE_ROLE, "parent"}
        and entry.body.phase == PROMPT_MESSAGE_PHASE
        and entry.body.content.text.strip() == delivered_prompt.strip()
    )


def _assignment_for_reference(
    snapshot: SessionSnapshot,
    reference: refs.AssignmentRef,
) -> AssignmentState | None:
    assignments = [
        assignment_state
        for assignment_state in snapshot.assignments()
        if assignment_state.assignment_id == reference.assignment_id
    ]
    return _one(assignments, f"assignment {reference.assignment_id!r}")


def _claude_assignment_turn(
    snapshot: SessionSnapshot,
    actor_reference: refs.ActorRef,
    assignment: AssignmentState,
    requested_prompt: str,
) -> refs.TurnRef | None:
    delivered_prompt = assignment.requested_prompt or requested_prompt
    prompts = [
        entry
        for entry in snapshot.entries
        if _matches_assignment_prompt(entry, actor_reference, assignment, delivered_prompt)
    ]
    prompt = _one(prompts, f"prompt for actor {actor_reference.actor_id!r}")
    if prompt is None or not isinstance(prompt.body, MessageBodyResponse):
        return None
    actor_state = snapshot.actor(actor_reference.actor_id)
    return refs.TurnRef(
        session=actor_reference.session,
        prompt=delivered_prompt,
        cursor_before=assignment.started_cursor,
        expected_prompt_count=actor_state.statistics.prompt_count,
        actor_id=actor_reference.actor_id,
        turn_id=prompt.turn_id,
        prompt_cursor=prompt.cursor,
        prompt_message_id=prompt.body.message_id,
        start_cursor=prompt.cursor,
    )


def _direct_assignment_turn(
    snapshot: SessionSnapshot,
    actor_reference: refs.ActorRef,
    assignment: AssignmentState,
    requested_prompt: str,
) -> refs.TurnRef | None:
    if assignment.turn_id is None:
        return None
    actor_state = snapshot.actor(actor_reference.actor_id)
    return refs.TurnRef(
        session=actor_reference.session,
        prompt=requested_prompt,
        cursor_before=assignment.started_cursor - 1,
        expected_prompt_count=actor_state.statistics.prompt_count,
        actor_id=actor_reference.actor_id,
        turn_id=assignment.turn_id,
        start_cursor=assignment.started_cursor,
    )


def _find_actor_assignment_turn(
    snapshot: SessionSnapshot,
    actor_reference: refs.ActorRef,
    assignment_reference: refs.AssignmentRef,
    requested_prompt: str,
) -> refs.TurnRef | None:
    assignment = _assignment_for_reference(snapshot, assignment_reference)
    if assignment is None or assignment.actor_id is None:
        return None
    if assignment.actor_id != actor_reference.actor_id:
        message = (
            f"assignment {assignment.assignment_id!r} belongs to actor "
            f"{assignment.actor_id!r}, not {actor_reference.actor_id!r}"
        )
        raise AssertionError(message)
    if snapshot.session_data.session.harness == "claude_code":
        return _claude_assignment_turn(
            snapshot,
            actor_reference,
            assignment,
            requested_prompt,
        )
    return _direct_assignment_turn(
        snapshot,
        actor_reference,
        assignment,
        requested_prompt,
    )


def actor_assignment_turn(
    watch: SessionWatch,
    *,
    actor_reference: refs.ActorRef,
    assignment_reference: refs.AssignmentRef,
    requested_prompt: str,
    timeout: float,
) -> refs.TurnRef:
    """Find the child turn for an actor assignment.

    Returns:
        The child turn reference.

    """
    return watch.wait(
        f"assignment {assignment_reference.assignment_id!r} to identify its child turn",
        partial(
            _find_actor_assignment_turn,
            actor_reference=actor_reference,
            assignment_reference=assignment_reference,
            requested_prompt=requested_prompt,
        ),
        timeout=timeout,
    )
