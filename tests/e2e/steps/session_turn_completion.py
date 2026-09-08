# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check turn completion and order."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from api.sessiondata.models.entry import TurnFinishedBodyResponse
from tests.e2e.testkit import references as refs, selector_turns, turns as turn_checks

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit import policy


def _completion_cursor(snapshot: SessionSnapshot, reference: refs.TurnRef, turn_name: str) -> int | None:
    completions = [
        entry.cursor
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and entry.turn_id == reference.turn_id
        and isinstance(entry.body, TurnFinishedBodyResponse)
    ]
    if len(completions) > 1:
        message = f"turn {turn_name!r} has {len(completions)} completion facts"
        raise AssertionError(message)
    return completions[0] if completions else None


@then(parsers.parse('turn "{name}" completes'))
def turn_completes(
    client: BaqylauClient,
    turns: refs.Turns,
    wait_policy: policy.WaitPolicy,
    name: str,
) -> None:
    """Wait until one turn completes."""
    current = turn_checks.wait_until_complete(
        client,
        turns.get(name),
        name=name,
        timeout=wait_policy.turn,
    )
    turns.replace(name, current)


@then(parsers.parse('turn "{name}" has state {state}'))
def turn_has_state(
    client: BaqylauClient,
    turns: refs.Turns,
    wait_policy: policy.WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Check one turn state."""
    current = turns.get(name)
    watch = client.sessions.watch(current.session)
    current = selector_turns.turn(watch, current, wait_policy.turn)
    turns.replace(name, current)
    assert current.turn_id is not None
    watch.wait(
        f"turn {name!r} to have state {state!r}",
        lambda snapshot: True if snapshot.turn_state(current.turn_id or "") == state else None,
        timeout=wait_policy.turn,
    )


@then(
    parsers.parse(
        'message from "{prompt_name}" enters the chat before response to "{turn_name}" finishes',
    ),
)
def message_enters_before_response_finishes(
    client: BaqylauClient,
    turns: refs.Turns,
    wait_policy: policy.WaitPolicy,
    prompt_name: str,
    turn_name: str,
) -> None:
    """Check that a prompt starts before another turn completes."""
    prompt = turn_checks.resolved(client, turns.get(prompt_name), timeout=wait_policy.feed)
    turn = turn_checks.resolved(client, turns.get(turn_name), timeout=wait_policy.feed)
    turns.replace(prompt_name, prompt)
    turns.replace(turn_name, turn)
    message = "turn order requires resolved prompt and turn identities"
    assert prompt.prompt_cursor is not None, message
    assert turn.turn_id is not None, message
    completed_at = client.sessions.watch(turn.session).wait(
        f"turn {turn_name!r} to complete",
        partial(_completion_cursor, reference=turn, turn_name=turn_name),
        timeout=wait_policy.turn,
    )
    assert prompt.prompt_cursor < completed_at, (
        f"turn {prompt_name!r} prompt was recorded at {prompt.prompt_cursor}; "
        f"turn {turn_name!r} completed at {completed_at}"
    )


@then(
    parsers.parse(
        'turn "{later_name}" starts after turn "{earlier_name}" completes',
    ),
)
def turn_starts_after_turn_completes(
    client: BaqylauClient,
    turns: refs.Turns,
    wait_policy: policy.WaitPolicy,
    later_name: str,
    earlier_name: str,
) -> None:
    """Check that a later turn starts after an earlier turn completes."""
    earlier = turn_checks.resolved(client, turns.get(earlier_name), timeout=wait_policy.turn)
    later = turn_checks.resolved(client, turns.get(later_name), timeout=wait_policy.turn)
    message = "turn order requires resolved turn identities"
    assert earlier.turn_id is not None, message
    assert later.activity_cursor is not None, message
    snapshot = client.sessions.snapshot(earlier.session)
    finished = [
        entry
        for entry in snapshot.entries
        if entry.actor_id == earlier.actor_id
        and entry.turn_id == earlier.turn_id
        and isinstance(entry.body, TurnFinishedBodyResponse)
    ]
    assert len(finished) == 1, f"turn {earlier_name!r} has {len(finished)} completion facts"
    assert finished[0].cursor < later.activity_cursor, (
        f"turn {later_name!r} started at {later.activity_cursor} before "
        f"turn {earlier_name!r} completed at {finished[0].cursor}"
    )
