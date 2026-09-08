# Copyright (c) 2026 Zhambyl Yermagambet
"""Read work-assignment state from one session snapshot."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sdk.state import AssignmentState, SessionSnapshot
    from tests.e2e.testkit.references import WorkRef


def completed_assignment(snapshot: SessionSnapshot, work: WorkRef, name: str) -> bool | None:
    """Return true when one assignment completed successfully.

    Returns:
        True after successful completion, or None while completion is pending.

    Raises:
        AssertionError: If the assignment has a state other than success or pending.

    """
    assignment = _assignment(snapshot, work)
    if assignment.state is None:
        return None
    if assignment.state == "succeeded":
        if assignment.finished_cursor is None:
            return None
        return True
    msg = f"subagent work {name!r} completed with state {assignment.state!r}"
    raise AssertionError(msg)


def assignment_has_state(snapshot: SessionSnapshot, work: WorkRef, state: str) -> bool | None:
    """Return true when one assignment has the requested state.

    Returns:
        True when one assignment has the requested state.

    """
    return True if _assignment(snapshot, work).state == state else None


def running_subagent_has_lead_status(
    snapshot: SessionSnapshot,
    work: WorkRef,
    status: str,
) -> bool | None:
    """Return true when a running subagent leaves the lead in one state.

    Returns:
        True when a running subagent leaves the lead in one state.

    """
    assignment = _assignment(snapshot, work)
    worker = snapshot.actor(work.worker.actor_id)
    if assignment.state is not None or worker.state != "running":
        return None
    return True if snapshot.lead().status == status else None


def work_has_state(snapshot: SessionSnapshot, work: WorkRef, state: str) -> bool | None:
    """Return true when the assigned or lead work has the requested state.

    Returns:
        True when the assigned or lead work has the requested state.

    """
    if work.turn.turn_id is not None:
        return True if snapshot.turn_state(work.turn.turn_id) == state else None
    if state != "aborted" or work.assignment is None:
        return None
    return True if _assignment(snapshot, work).state in {"cancelled", "failed"} else None


def released_lead(snapshot: SessionSnapshot, work: WorkRef, name: str) -> bool | None:
    """Return true when work release left the lead ready for a response.

    Returns:
        True when the lead is ready for a response, or None while it is not ready.

    Raises:
        AssertionError: If the assignment completed without success.

    """
    lead = snapshot.lead()
    if work.assignment is None:
        return True if lead.status == "awaiting_response" and not lead.statistics.active else None
    assignment = _assignment(snapshot, work)
    if assignment.state is not None and assignment.state != "succeeded":
        msg = f"subagent work {name!r} has assignment state {assignment.state!r}"
        raise AssertionError(msg)
    if assignment.state != "succeeded" or assignment.finished_cursor is None:
        return None
    return True if lead.status == "awaiting_response" and not lead.statistics.active else None


def assignment_result(snapshot: SessionSnapshot, work: WorkRef) -> str:
    """Return the final result text for one assignment.

    Returns:
        The final result text for one assignment.

    """
    return _assignment(snapshot, work).result


def _assignment(snapshot: SessionSnapshot, work: WorkRef) -> AssignmentState:
    """Return the one assignment state represented by work.

    Returns:
        The one assignment state represented by work.

    Raises:
        AssertionError: If the work has no assignment or does not match exactly one assignment.

    """
    if work.assignment is None:
        msg = "lead work does not have an assignment"
        raise AssertionError(msg)
    matches = [
        assignment_state
        for assignment_state in snapshot.assignments()
        if assignment_state.assignment_id == work.assignment.assignment_id
    ]
    if len(matches) != 1:
        assignment_id = work.assignment.assignment_id
        match_count = len(matches)
        msg = f"work assignment {assignment_id!r} has {match_count} matches"
        raise AssertionError(
            msg,
        )
    return matches[0]
