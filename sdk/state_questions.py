# Copyright (c) 2026 Zhambyl Yermagambet
"""Materialize question state from session entries."""

from __future__ import annotations

from api.sessiondata.models import entry as entry_models
from sdk.state_models import QuestionState


def questions(entries: tuple[entry_models.EntryResponse, ...]) -> tuple[QuestionState, ...]:
    """Return materialized questions.

    Returns:
        Materialized questions.

    """
    folded: dict[str, QuestionState] = {}
    for entry in entries:
        _fold_entry(folded, entry)
    return tuple(folded.values())


def _fold_entry(folded: dict[str, QuestionState], entry: entry_models.EntryResponse) -> None:
    body = entry.body
    if isinstance(body, entry_models.QuestionAskedBodyResponse):
        folded[body.attention_id] = QuestionState(
            attention_id=body.attention_id,
            actor_id=entry.actor_id,
            turn_id=entry.turn_id,
            questions=body.questions,
            asked_cursor=entry.cursor,
        )
    elif isinstance(body, entry_models.QuestionAnsweredBodyResponse):
        _finish(folded, body)


def _finish(folded: dict[str, QuestionState], body: entry_models.QuestionAnsweredBodyResponse) -> None:
    found = folded.get(body.attention_id)
    if found is not None:
        found.answers = body.answers
        found.feedback = body.feedback
