# Copyright (c) 2026 Zhambyl Yermagambet
"""Named compaction acquisition and lifecycle checks."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.steps import compaction_checks
from tests.e2e.testkit import selector_progress

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.observation_contexts import CompactionObservationContext
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Compactions


@when(
    parsers.parse(
        'I name the compaction in session "{session_name}" after control "{control_name}" "{compaction_name}"',
    ),
)
def name_compaction(
    compaction_observation_context: CompactionObservationContext,
    session_name: str,
    control_name: str,
    compaction_name: str,
) -> None:
    """Process name compaction."""
    control = compaction_observation_context.controls.get(control_name)
    found = selector_progress.compaction(
        compaction_observation_context.client.sessions.watch(
            compaction_observation_context.sessions.get(session_name),
        ),
        after_cursor=control.cursor_before,
        timeout=compaction_observation_context.wait_policy.background,
    )
    compaction_observation_context.compactions.bind(compaction_name, found)


@then(parsers.parse('compaction "{name}" finishes'))
def compaction_finishes(
    client: BaqylauClient,
    compactions: Compactions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Process compaction finishes."""
    reference = compactions.get(name)
    client.sessions.watch(reference.session).wait(
        f"compaction {name!r} to finish",
        partial(compaction_checks.is_finished, reference=reference),
        timeout=wait_policy.background,
    )


@then(parsers.parse('compaction "{name}" leaves its actor ready'))
def compaction_leaves_actor_ready(
    client: BaqylauClient,
    compactions: Compactions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Process compaction leaves actor ready."""
    reference = compactions.get(name)
    client.sessions.watch(reference.session).wait(
        f"compaction {name!r} actor to leave compacting state",
        partial(compaction_checks.actor_is_ready, reference=reference),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('compaction "{name}" has one finished feed entry'))
def compaction_has_one_finished_feed_entry(
    client: BaqylauClient,
    compactions: Compactions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Process compaction has one finished feed entry."""
    reference = compactions.get(name)
    client.sessions.watch(reference.session).wait(
        f"compaction {name!r} to have one finished feed entry",
        partial(compaction_checks.has_one_finished_entry, reference=reference, name=name),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('compaction "{name}" has expandable compacted context'))
def compaction_has_compacted_context(
    client: BaqylauClient,
    compactions: Compactions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Process compaction has compacted context."""
    reference = compactions.get(name)
    client.sessions.watch(reference.session).wait(
        f"compaction {name!r} to have expandable compacted context",
        partial(compaction_checks.has_context, reference=reference, name=name),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('compaction "{name}" has no expandable compacted context'))
def compaction_has_no_compacted_context(
    client: BaqylauClient,
    compactions: Compactions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Process compaction has no compacted context."""
    reference = compactions.get(name)
    client.sessions.watch(reference.session).wait(
        f"compaction {name!r} to have no expandable compacted context",
        partial(compaction_checks.has_no_context, reference=reference, name=name),
        timeout=wait_policy.feed,
    )
