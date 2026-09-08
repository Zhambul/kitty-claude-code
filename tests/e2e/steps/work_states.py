# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check worker type, state, and resource use."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import work_assertions

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Works


@then(parsers.parse('work "{name}" has positive context use'))
def work_has_positive_context_use(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Check that work reports context use."""
    work = works.get(name)
    client.sessions.watch(work.session).wait(
        f"work {name!r} to report positive context use",
        lambda snapshot: (
            True
            if snapshot.actor(work.worker.actor_id).context.used_tokens > 0
            and snapshot.actor(work.worker.actor_id).context.window_tokens > 0
            else None
        ),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('work "{name}" context use does not exceed its window'))
def work_context_use_does_not_exceed_window(
    client: BaqylauClient,
    works: Works,
    name: str,
) -> None:
    """Check that context use is within its window."""
    work = works.get(name)
    context = client.sessions.snapshot(work.session).actor(work.worker.actor_id).context
    assert 0 < context.used_tokens <= context.window_tokens


@then(parsers.parse('subagent work "{name}" has assignment state {state}'))
def subagent_work_has_assignment_state(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Check one subagent assignment state."""
    work = works.get(name)
    client.sessions.watch(work.session).wait(
        f"subagent work {name!r} to have assignment state {state!r}",
        partial(work_assertions.assignment_has_state, work=work, state=state),
        timeout=wait_policy.background,
    )


@then(
    parsers.parse(
        'subagent work "{name}" is running while its lead has status {status}',
    ),
)
def running_subagent_has_lead_status(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
    status: str,
) -> None:
    """Check a running subagent and its lead status.

    Raises:
        AssertionError: If the work is not a subagent work item.

    """
    work = works.get(name)
    if work.assignment is None:
        message = f"work {name!r} is not subagent work"
        raise AssertionError(message)
    client.sessions.watch(work.session).wait(
        f"subagent work {name!r} to run while its lead has status {status!r}",
        partial(work_assertions.running_subagent_has_lead_status, work=work, status=status),
        timeout=wait_policy.background,
    )


@then(parsers.parse('work "{name}" has state {state}'))
def work_has_state(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Check one work state."""
    work = works.get(name)
    client.sessions.watch(work.session).wait(
        f"work {name!r} to have state {state!r}",
        partial(work_assertions.work_has_state, work=work, state=state),
        timeout=wait_policy.turn,
    )


@then(parsers.parse("subagent work \"{name}\" has assignment result containing '{text}'"))
def subagent_work_has_assignment_result(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
    text: str,
) -> None:
    """Check part of one subagent assignment result."""
    work = works.get(name)
    client.sessions.watch(work.session).wait(
        f"subagent work {name!r} result to contain {text!r}",
        lambda snapshot: True if text in work_assertions.assignment_result(snapshot, work) else None,
        timeout=wait_policy.background,
    )


@then(parsers.parse('work "{name}" releases the lead'))
def work_releases_lead(
    client: BaqylauClient,
    works: Works,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Check that work releases its lead."""
    work = works.get(name)
    client.sessions.watch(work.session).wait(
        f"work {name!r} to finish its assignment and release the lead",
        partial(work_assertions.released_lead, work=work, name=name),
        timeout=wait_policy.turn,
    )
