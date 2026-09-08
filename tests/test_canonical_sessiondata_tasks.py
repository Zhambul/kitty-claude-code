# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata tasks."""

from __future__ import annotations

import pytest

from tests import (
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_folding as folding,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain


@pytest.mark.parametrize(("state", "reason"), [
    (session_domain.work_state.GoalState.ACTIVE, None),
    (session_domain.work_state.GoalState.BLOCKED, "waiting for access"),
    (session_domain.work_state.GoalState.COMPLETED, None),
])
def test_goal_keeps_its_state_and_reason(state: session_domain.work_state.GoalState, reason: str | None) -> None:
    """Keep each goal state and its reason."""
    goal = folding.session_after(
        *session_fixtures.alive(),
        session_domain.event_work.GoalChanged(
            session_values.SHIP_PROMPT, state, reason,
        ),
    ).goal
    assert goal is not None
    assert (goal.state, goal.reason) == (state, reason)


def test_cleared_goal_is_absent() -> None:
    """Remove an active goal when it is cleared."""
    assert (
        folding.session_after(
            *session_fixtures.alive(),
            session_domain.event_work.GoalChanged(
                session_values.SHIP_PROMPT, session_domain.work_state.GoalState.ACTIVE, None,
            ),
            session_domain.event_work.GoalChanged(None, session_domain.work_state.GoalState.CLEARED, None),
        ).goal
        is None
    )


def test_list_fact_orders_tasks_and_decides_which() -> None:
    """Verify the list fact orders the tasks and decides which belong.

    Two facts, two jobs: what a task IS, and which tasks there are. A task the
        list stopped naming is gone from it even though its own last state stands.
    """
    first = session_domain.event_work.TaskChanged(
        session_values.FIRST_TASK_ID,
        session_values.FIRST_TASK_TEXT,
        None,
        session_domain.work_state.TaskState.COMPLETED,
        session_values.LEAD,
    )
    second = session_domain.event_work.TaskChanged(
        session_values.SECOND_TASK_ID,
        "Change it",
        None,
        session_domain.work_state.TaskState.IN_PROGRESS,
        session_values.LEAD,
    )
    state = folding.fold(
        *session_fixtures.alive(),
        second,
        first,
        session_domain.event_work.TaskListChanged(
            session_values.TASK_LIST_ID,
            (session_values.FIRST_TASK_ID, session_values.SECOND_TASK_ID),
        ),
    )
    task_subjects = [task.subject for task in folding.session_from(state).tasks]
    assert task_subjects == [session_values.FIRST_TASK_TEXT, "Change it"]

    dropped = folding.fold(
        *session_fixtures.alive(),
        first,
        second,
        session_domain.event_work.TaskListChanged(session_values.TASK_LIST_ID, (session_values.SECOND_TASK_ID,)),
    )
    assert [task.task_id for task in folding.session_from(dropped).tasks] == [session_values.SECOND_TASK_ID]


def test_task_nobody_has_listed_yet_still_belongs() -> None:
    """Verify a task nobody has listed yet still belongs to the session."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_work.TaskChanged(
            session_values.FIRST_TASK_ID,
            session_values.FIRST_TASK_TEXT,
            None,
            session_domain.work_state.TaskState.PENDING,
            None,
        ),
    )
    assert [task.task_id for task in folding.session_from(state).tasks] == [session_values.FIRST_TASK_ID]
