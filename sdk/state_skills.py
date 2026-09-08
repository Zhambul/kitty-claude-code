# Copyright (c) 2026 Zhambyl Yermagambet
"""Materialize skill state from session entries."""

from __future__ import annotations

from api.sessiondata.models import entry as entry_models
from sdk.state_models import SkillState


def skills(entries: tuple[entry_models.EntryResponse, ...]) -> tuple[SkillState, ...]:
    """Return materialized skills.

    Returns:
        Materialized skills.

    """
    folded: dict[str, SkillState] = {}
    for entry in entries:
        _fold_entry(folded, entry)
    return tuple(folded.values())


def _fold_entry(folded: dict[str, SkillState], entry: entry_models.EntryResponse) -> None:
    body = entry.body
    if isinstance(body, entry_models.SkillStartedBodyResponse):
        folded[body.skill_id] = SkillState(
            skill_id=body.skill_id,
            actor_id=entry.actor_id,
            turn_id=entry.turn_id,
            name=body.name,
            arguments="" if body.arguments is None else body.arguments.text,
            started_cursor=entry.cursor,
        )
    elif isinstance(body, entry_models.SkillFinishedBodyResponse):
        _finish(folded, body)


def _finish(folded: dict[str, SkillState], body: entry_models.SkillFinishedBodyResponse) -> None:
    found = folded.get(body.skill_id)
    if found is not None:
        found.state = body.state
        found.result = "" if body.result is None else body.result.text
