# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check assignments from child actor work."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import assignment_counts, assignment_states

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Assignments, Turns


@then(parsers.parse('assignment "{name}" has state {state}'))
def assignment_has_state(
    client: BaqylauClient,
    assignments: Assignments,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Wait for one assignment state."""
    reference = assignments.get(name)
    client.sessions.watch(reference.session).wait(
        f"assignment {name!r} to have state {state!r}",
        partial(assignment_states.has_state, reference=reference, state=state),
        timeout=wait_policy.feed,
    )


@then(parsers.parse("assignment \"{name}\" has result containing '{text}'"))
def assignment_has_result(
    client: BaqylauClient,
    assignments: Assignments,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Wait for text in one assignment result."""
    reference = assignments.get(name)
    client.sessions.watch(reference.session).wait(
        f"assignment {name!r} result to contain {text!r}",
        partial(assignment_states.result_contains, reference=reference, text=text),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('turn "{turn_name}" has exactly {count:d} assignments'))
def turn_has_assignment_count(
    client: BaqylauClient,
    turns: Turns,
    wait_policy: WaitPolicy,
    turn_name: str,
    count: int,
) -> None:
    """Wait for the required assignment count in one turn."""
    turn = turns.get(turn_name)
    client.sessions.watch(turn.session).wait(
        f"turn {turn_name!r} to have exactly {count} assignments",
        partial(assignment_counts.has_turn_count, reference=turn, count=count, name=turn_name),
        timeout=wait_policy.feed,
    )
