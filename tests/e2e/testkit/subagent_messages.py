# Copyright (c) 2026 Zhambyl Yermagambet
"""Check evidence that a child actor received a follow-up."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models.entry import EntryResponse, MessageBodyResponse
from tests.e2e.testkit.turns import matches_final_answer

if TYPE_CHECKING:
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit import references as refs


def followup_was_observed(
    snapshot: SessionSnapshot,
    work: refs.WorkRef,
    lead_actor_id: str,
    answer_after: int,
    text: str,
) -> bool | None:
    """Return true when the child receives a message or gives its answer.

    Returns:
        True for durable evidence, else None.

    """
    sent = [
        entry
        for entry in snapshot.entries
        if entry.actor_id == lead_actor_id
        and isinstance(entry.body, MessageBodyResponse)
        and entry.body.recipient_actor_id == work.worker.actor_id
        and entry.body.content.text == text
    ]
    answered = [entry for entry in snapshot.entries if _matches_assignment_answer(entry, work, answer_after, text)]
    return True if sent or answered else None


def _matches_assignment_answer(
    entry: EntryResponse,
    work: refs.WorkRef,
    answer_after: int,
    text: str,
) -> bool:
    if entry.cursor <= answer_after or entry.actor_id != work.worker.actor_id:
        return False
    if not isinstance(entry.body, MessageBodyResponse):
        return False
    return (
        entry.body.role == "assistant"
        and entry.body.phase == "end_turn"
        and matches_final_answer(entry.body.content.text, text)
    )
