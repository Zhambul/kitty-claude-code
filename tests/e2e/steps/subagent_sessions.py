# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check child actor state in sessions."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import subagent_states

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Actors, Sessions


@then(parsers.parse('actor "{name}" has state {state}'))
def actor_has_state(
    client: BaqylauClient,
    actors: Actors,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Wait for one actor state."""
    reference = actors.get(name)
    client.sessions.watch(reference.session).wait(
        f"actor {name!r} to have state {state!r}",
        partial(subagent_states.actor_has_state, reference=reference, state=state),
        timeout=wait_policy.background,
    )


@then(parsers.parse('session "{session_name}" has exactly {count:d} subagents'))
def session_has_subagent_count(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    session_name: str,
    count: int,
) -> None:
    """Wait for the required child actor count."""
    session = sessions.get(session_name)
    client.sessions.watch(session).wait(
        f"session {session_name!r} to have exactly {count} subagents",
        partial(subagent_states.has_count, count=count, session_name=session_name),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('every subagent in session "{session_name}" has state {state}'))
def every_subagent_has_state(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    session_name: str,
    state: str,
) -> None:
    """Wait for all child actors to have one state."""
    session = sessions.get(session_name)
    client.sessions.watch(session).wait(
        f"every subagent in session {session_name!r} to have state {state!r}",
        partial(subagent_states.all_have_state, state=state),
        timeout=wait_policy.background,
    )


@then(parsers.parse("the lead actor in session \"{session_name}\" has no command containing '{command}'"))
def lead_has_no_command(
    client: BaqylauClient,
    sessions: Sessions,
    session_name: str,
    command: str,
) -> None:
    """Check that the lead actor does not have a matching command."""
    snapshot = client.sessions.snapshot(sessions.get(session_name))
    found = [shell_state.command for shell_state in snapshot.shells(actor_id=snapshot.lead().actor_id)]
    assert not any(command in shell_command for shell_command in found), (
        f"lead actor has a command containing {command!r}: {found}"
    )
