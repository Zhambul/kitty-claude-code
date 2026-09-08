# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check session goals."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from domain.work_state import GoalState

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit import references as refs
    from tests.e2e.testkit.policy import WaitPolicy


@then(parsers.parse("session \"{name}\" has goal '{objective}'"))
def session_has_goal(
    client: BaqylauClient,
    sessions: refs.Sessions,
    wait_policy: WaitPolicy,
    name: str,
    objective: str,
) -> None:
    """Wait for a session goal with one objective."""
    session = sessions.get(name)
    client.sessions.watch(session).wait(
        f"session {name!r} to have goal {objective!r}",
        lambda snapshot: (
            True
            if snapshot.session_data.session.goal is not None
            and snapshot.session_data.session.goal.objective == objective
            else None
        ),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('the goal in session "{name}" is complete'))
def session_goal_is_complete(
    client: BaqylauClient,
    sessions: refs.Sessions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Wait for a completed session goal."""
    session = sessions.get(name)
    client.sessions.watch(session).wait(
        f"the goal in session {name!r} to be complete",
        lambda snapshot: (
            True
            if snapshot.session_data.session.goal is not None and snapshot.session_data.session.goal.completed
            else None
        ),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('the goal in session "{name}" has state {state}'))
def session_goal_has_state(
    client: BaqylauClient,
    sessions: refs.Sessions,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Wait for a session goal state.

    Raises:
        AssertionError: If the requested state is not valid.

    """
    try:
        expected = GoalState(state)
    except ValueError:
        message = f"unknown goal state {state!r}"
        raise AssertionError(message) from None
    session = sessions.get(name)
    client.sessions.watch(session).wait(
        f"the goal in session {name!r} to have state {state!r}",
        lambda snapshot: (
            True
            if snapshot.session_data.session.goal is not None and snapshot.session_data.session.goal.state == expected
            else None
        ),
        timeout=wait_policy.feed,
    )
