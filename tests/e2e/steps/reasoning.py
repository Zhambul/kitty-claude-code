# Copyright (c) 2026 Zhambyl Yermagambet
"""Named reasoning-trace acquisition and checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from api.sessiondata.models.entry import ReasoningBodyResponse
from tests.e2e.testkit import selector_changes

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.observation_contexts import WorkObservationContext
    from tests.e2e.testkit.references import ReasoningTraceRef, ReasoningTraces


def _parts(
    snapshot: SessionSnapshot,
    reference: ReasoningTraceRef,
) -> tuple[ReasoningBodyResponse, ...]:
    by_id = {entry.entry_id: entry for entry in snapshot.entries}
    found: list[ReasoningBodyResponse] = []
    for entry_id in reference.entry_ids:
        entry = by_id.get(entry_id)
        if entry is None or not isinstance(entry.body, ReasoningBodyResponse):
            message = f"reasoning entry {entry_id!r} is absent"
            raise AssertionError(message)
        if entry.actor_id != reference.actor_id:
            message = f"reasoning entry {entry_id!r} belongs to actor {entry.actor_id!r}"
            raise AssertionError(
                message,
            )
        found.append(entry.body)
    return tuple(found)


@when(
    parsers.parse(
        'I name the reasoning trace in work "{work_name}" "{trace_name}"',
    ),
)
def name_reasoning_trace(
    reasoning_observation_context: WorkObservationContext[ReasoningTraceRef],
    work_name: str,
    trace_name: str,
) -> None:
    """Process name reasoning trace."""
    work = reasoning_observation_context.works.get(work_name)
    reasoning_observation_context.references.bind(
        trace_name,
        selector_changes.reasoning_trace(
            reasoning_observation_context.client.sessions.watch(work.session),
            turn_reference=work.turn,
            timeout=reasoning_observation_context.wait_policy.feed,
        ),
    )


@then(parsers.parse('reasoning trace "{name}" has at least {count:d} part'))
def reasoning_trace_has_parts(
    client: BaqylauClient,
    reasoning_traces: ReasoningTraces,
    name: str,
    count: int,
) -> None:
    """Process reasoning trace has parts."""
    reference = reasoning_traces.get(name)
    parts = _parts(client.sessions.snapshot(reference.session), reference)
    assert len(parts) >= count, f"reasoning trace {name!r} has {len(parts)} parts"


@then(parsers.parse('each part of reasoning trace "{name}" contains text'))
def reasoning_trace_parts_contain_text(
    client: BaqylauClient,
    reasoning_traces: ReasoningTraces,
    name: str,
) -> None:
    """Process reasoning trace parts contain text."""
    reference = reasoning_traces.get(name)
    parts = _parts(client.sessions.snapshot(reference.session), reference)
    empty: list[int] = []
    for index, part in enumerate(parts):
        if not part.content.text.strip():
            empty.append(index)
    assert not empty, f"reasoning trace {name!r} has empty parts at indexes {empty}"
