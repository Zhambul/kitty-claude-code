# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable reasoning and worktree references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import ReasoningBodyResponse, WorktreeBodyResponse
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one, belongs_to_turn

if TYPE_CHECKING:
    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot


def _find_reasoning_trace(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
) -> refs.ReasoningTraceRef | None:
    entries = tuple(
        entry
        for entry in snapshot.entries
        if isinstance(entry.body, ReasoningBodyResponse)
        and entry.actor_id == turn_reference.actor_id
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=entry.turn_id,
            cursor=entry.cursor,
        )
    )
    if not entries:
        return None
    return refs.ReasoningTraceRef(
        snapshot.session_reference,
        turn_reference.actor_id or "",
        tuple(entry.entry_id for entry in entries),
    )


def reasoning_trace(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    timeout: float,
) -> refs.ReasoningTraceRef:
    """Find the reasoning trace for a turn.

    Returns:
        The reasoning trace reference.

    Raises:
        AssertionError: If the turn has no actor identity.

    """
    if turn_reference.actor_id is None:
        message = "reasoning trace requires a resolved actor"
        raise AssertionError(message)

    return watch.wait(
        "at least one reasoning entry",
        partial(_find_reasoning_trace, turn_reference=turn_reference),
        timeout=timeout,
    )


def _find_worktree_change(
    snapshot: SessionSnapshot,
    turn_reference: refs.TurnRef,
    action: str,
) -> refs.WorktreeChangeRef | None:
    candidates = [
        entry
        for entry in snapshot.entries
        if isinstance(entry.body, WorktreeBodyResponse)
        and entry.body.action == action
        and belongs_to_turn(
            snapshot,
            turn_reference,
            turn_id=entry.turn_id,
            cursor=entry.cursor,
        )
    ]
    entry = _one(candidates, f"worktree change with action {action!r}")
    if entry is None:
        return None
    return refs.WorktreeChangeRef(snapshot.session_reference, entry.entry_id)


def worktree_change(
    watch: SessionWatch,
    *,
    turn_reference: refs.TurnRef,
    action: str,
    timeout: float,
) -> refs.WorktreeChangeRef:
    """Find one worktree change in a turn.

    Returns:
        The worktree change reference.

    """
    return watch.wait(
        f"one worktree change with action {action!r}",
        partial(
            _find_worktree_change,
            turn_reference=turn_reference,
            action=action,
        ),
        timeout=timeout,
    )
