# Copyright (c) 2026 Zhambyl Yermagambet
"""Check assignment counts in one session turn."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit import selector_common

if TYPE_CHECKING:
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.references import TurnRef


def has_turn_count(
    snapshot: SessionSnapshot,
    reference: TurnRef,
    count: int,
    name: str,
) -> bool | None:
    """Return true when a turn has the required assignment count.

    Returns:
        True for the required count, else None.

    Raises:
        AssertionError: If the turn has more assignments than required.

    """
    assignments = [
        assignment_state
        for assignment_state in snapshot.assignments()
        if assignment_state.turn_id == reference.turn_id
        or selector_common.cursor_is_in_turn(snapshot, reference, assignment_state.started_cursor)
    ]
    if len(assignments) > count:
        message = f"turn {name!r} has {len(assignments)} assignments: {assignments}"
        raise AssertionError(message)
    return True if len(assignments) == count else None
