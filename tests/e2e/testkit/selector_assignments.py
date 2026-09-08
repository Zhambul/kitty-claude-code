# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable assignment references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one, belongs_to_turn

if TYPE_CHECKING:
    from sdk.client import SessionWatch
    from sdk.state import AssignmentState, SessionSnapshot


def _find_assignment(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    exact_actor_name: str | None,
    exact_prompt: str | None,
) -> refs.AssignmentRef | None:
    candidates = [
        assignment_state
        for assignment_state in snapshot.assignments()
        if belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=assignment_state.turn_id,
            cursor=assignment_state.started_cursor,
        )
        and (
            exact_actor_name is None
            or (assignment_state.assigned_actor_name or "").casefold() == exact_actor_name.casefold()
        )
        and (exact_prompt is None or (assignment_state.requested_prompt or "").strip() == exact_prompt.strip())
    ]
    assignment_state: AssignmentState | None = _one(candidates, "agent assignment")
    if assignment_state is None:
        return None
    return refs.AssignmentRef(
        snapshot.session_reference,
        assignment_state.assignment_id,
    )


def assignment(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    exact_actor_name: str | None = None,
    exact_prompt: str | None = None,
    timeout: float,
) -> refs.AssignmentRef:
    """Find one assignment in a turn.

    Returns:
        The assignment reference.

    """
    return watch.wait(
        "one agent assignment in the named turn",
        partial(
            _find_assignment,
            turn_reference=turn_reference,
            exact_actor_name=exact_actor_name,
            exact_prompt=exact_prompt,
        ),
        timeout=timeout,
    )
