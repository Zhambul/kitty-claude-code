# Copyright (c) 2026 Zhambyl Yermagambet
"""Materialize compaction state from session entries."""

from __future__ import annotations

from api.sessiondata.models import entry as entry_models
from sdk.state_models import CompactionState


def compactions(entries: tuple[entry_models.EntryResponse, ...]) -> tuple[CompactionState, ...]:
    """Return materialized compactions.

    Returns:
        Materialized compactions.

    """
    found: list[CompactionState] = []
    open_by_actor: dict[str, CompactionState] = {}
    for entry in entries:
        body = entry.body
        if isinstance(body, entry_models.CompactionStartedBodyResponse):
            started = _started(entry, body)
            found.append(started)
            open_by_actor[entry.actor_id] = started
        elif isinstance(body, entry_models.CompactionFinishedBodyResponse):
            _finish(open_by_actor, entry, body)
    return tuple(found)


def _started(
    entry: entry_models.EntryResponse,
    body: entry_models.CompactionStartedBodyResponse,
) -> CompactionState:
    return CompactionState(
        actor_id=entry.actor_id,
        turn_id=entry.turn_id,
        started_cursor=entry.cursor,
        before_tokens=body.before_tokens,
    )


def _finish(
    open_by_actor: dict[str, CompactionState],
    entry: entry_models.EntryResponse,
    body: entry_models.CompactionFinishedBodyResponse,
) -> None:
    open_state = open_by_actor.pop(entry.actor_id, None)
    if open_state is None:
        return
    open_state.before_tokens = body.before_tokens
    open_state.after_tokens = body.after_tokens
    open_state.finished_cursor = entry.cursor
