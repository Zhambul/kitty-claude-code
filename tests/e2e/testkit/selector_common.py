# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared selection rules for stable test references."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models.entry import MessageBodyResponse

if TYPE_CHECKING:
    from collections.abc import Sequence

    from api.sessiondata.models.entry import EntryResponse
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit import references as refs

USER_MESSAGE_ROLE = "user"
PROMPT_MESSAGE_PHASE = "prompt"


def _one[SelectionT](selections: Sequence[SelectionT], description: str) -> SelectionT | None:
    if len(selections) > 1:
        message = f"{description} matched {len(selections)} objects: {selections}"
        raise AssertionError(message)
    return selections[0] if selections else None


def _is_actor_prompt_after(
    entry: EntryResponse,
    reference: refs.TurnRef,
    after_cursor: int,
) -> bool:
    if entry.cursor <= after_cursor or entry.actor_id != reference.actor_id:
        return False
    if not isinstance(entry.body, MessageBodyResponse):
        return False
    return entry.body.role in {USER_MESSAGE_ROLE, "parent"} and entry.body.phase == PROMPT_MESSAGE_PHASE


def next_prompt_cursor(
    snapshot: SessionSnapshot,
    reference: refs.TurnRef,
    *,
    after: int,
) -> int | None:
    """Find the next prompt cursor for the actor.

    Returns:
        The next prompt cursor, or ``None`` when there is no next prompt.

    Raises:
        AssertionError: If the turn has no actor identity.

    """
    if reference.actor_id is None:
        message = "turn does not have a resolved actor identity"
        raise AssertionError(message)
    found = [entry.cursor for entry in snapshot.entries if _is_actor_prompt_after(entry, reference, after)]
    return min(found) if found else None


def cursor_is_in_turn(snapshot: SessionSnapshot, reference: refs.TurnRef, cursor: int) -> bool:
    """Test if a cursor is in the turn.

    Returns:
        ``True`` when the cursor is in the turn.

    """
    start_cursor = reference.activity_cursor
    if start_cursor is None or cursor <= start_cursor:
        return False
    boundary = next_prompt_cursor(snapshot, reference, after=start_cursor)
    return boundary is None or cursor < boundary


def belongs_to_turn(
    snapshot: SessionSnapshot,
    reference: refs.TurnRef,
    *,
    turn_id: str | None,
    cursor: int,
) -> bool:
    """Test if an event belongs to the turn.

    Returns:
        ``True`` when the event belongs to the turn.

    """
    return turn_id == reference.turn_id or cursor_is_in_turn(snapshot, reference, cursor)
