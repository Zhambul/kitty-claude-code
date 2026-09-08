# Copyright (c) 2026 Zhambyl Yermagambet
"""Materialize plan state from session entries."""

from __future__ import annotations

from api.sessiondata.models import entry as entry_models
from sdk.state_models import PlanState


def plans(entries: tuple[entry_models.EntryResponse, ...]) -> tuple[PlanState, ...]:
    """Return materialized plans.

    Returns:
        Materialized plans.

    """
    folded: dict[str, PlanState] = {}
    for entry in entries:
        _fold_entry(folded, entry)
    return tuple(folded.values())


def _fold_entry(folded: dict[str, PlanState], entry: entry_models.EntryResponse) -> None:
    body = entry.body
    if isinstance(body, entry_models.PlanProposedBodyResponse):
        folded[body.attention_id] = PlanState(
            attention_id=body.attention_id,
            actor_id=entry.actor_id,
            turn_id=entry.turn_id,
            text=body.plan.text,
            proposed_cursor=entry.cursor,
        )
    elif isinstance(body, entry_models.PlanResolvedBodyResponse):
        _finish(folded, body)


def _finish(folded: dict[str, PlanState], body: entry_models.PlanResolvedBodyResponse) -> None:
    found = folded.get(body.attention_id)
    if found is not None and not _preserves_feedback(found, body):
        found.state = body.state
        found.feedback = body.feedback
        found.edited = body.edited


def _preserves_feedback(found: PlanState, body: entry_models.PlanResolvedBodyResponse) -> bool:
    has_feedback = found.state == "changes_requested" and bool(found.feedback)
    return has_feedback and body.state == "rejected" and not body.feedback
