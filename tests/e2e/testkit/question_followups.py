# Copyright (c) 2026 Zhambyl Yermagambet
"""Check messages that follow a question control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from api.sessiondata.models.entry import MessageBodyResponse
from tests.e2e.testkit import question_states, references as refs
from tests.e2e.testkit.turns import matches_final_answer

if TYPE_CHECKING:
    from api.sessiondata.models.entry import EntryResponse
    from sdk.state import QuestionState, SessionSnapshot


@dataclass(frozen=True)
class FollowupCriteria:
    """Describe one expected follow-up message."""

    cursor_before: int
    text: str
    role: str
    phase: str
    description: str


def has_followup(
    snapshot: SessionSnapshot,
    reference: refs.QuestionRef,
    criteria: FollowupCriteria,
) -> bool | None:
    """Return true when the question has one required follow-up.

    Returns:
        True for the required message, else None.

    Raises:
        AssertionError: If more than one matching message exists.

    """
    state, _prompt = question_states.question(snapshot, reference)
    messages = [entry for entry in snapshot.entries if _matches(entry, state, criteria)]
    if len(messages) > 1:
        message = f"{criteria.description} has {len(messages)} messages equal to {criteria.text!r}"
        raise AssertionError(message)
    return True if len(messages) == 1 else None


def _matches(entry: EntryResponse, state: QuestionState, criteria: FollowupCriteria) -> bool:
    if entry.cursor <= criteria.cursor_before or entry.actor_id != state.actor_id:
        return False
    if not isinstance(entry.body, MessageBodyResponse):
        return False
    return (
        entry.body.role == criteria.role
        and entry.body.phase == criteria.phase
        and matches_final_answer(entry.body.content.text, criteria.text)
    )
