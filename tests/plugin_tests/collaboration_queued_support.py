# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for queued turn tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    event_conversation,
    ids as domain_ids,
)
from tests.plugin_tests.collaboration_assertion_support import turn_id_of
from tests.plugin_tests.support_events import payloads

if TYPE_CHECKING:
    from harness.models.raw_events import (
        TranslationResult,
    )


def assert_queued_turn_sequence(
    first: TranslationResult,
    queued: TranslationResult,
    marker: TranslationResult,
    answer: TranslationResult,
    stopped: TranslationResult,
) -> None:
    """Check that a queued prompt starts a new turn and owns its completion."""
    first_turn = turn_id_of(first, event_conversation.TurnStarted)
    queued_turn = turn_id_of(queued, event_conversation.TurnStarted)
    assert_queued_turn_start(first_turn, queued_turn, queued)
    assert_queued_turn_completion(first_turn, queued_turn, marker, answer, stopped)


def assert_queued_turn_start(
    first_turn: domain_ids.TurnId | None,
    queued_turn: domain_ids.TurnId | None,
    queued: TranslationResult,
) -> None:
    """Verify that a queued prompt starts its own turn."""
    assert queued_turn is not None
    assert queued_turn != first_turn
    assert turn_id_of(queued, event_conversation.TurnAborted) == first_turn
    assert turn_id_of(queued, event_conversation.MessageCreated) == queued_turn


def assert_queued_turn_completion(
    first_turn: domain_ids.TurnId | None,
    queued_turn: domain_ids.TurnId | None,
    marker: TranslationResult,
    answer: TranslationResult,
    stopped: TranslationResult,
) -> None:
    """Verify that the queued turn owns its completion facts."""
    assert payloads(marker, event_conversation.TurnAborted) == []
    assert all(event.turn_id == first_turn for event in marker.canonical_events)
    assert turn_id_of(answer, event_conversation.MessageCreated) == queued_turn
    assert turn_id_of(answer, event_conversation.TurnFinished) == queued_turn
    assert turn_id_of(stopped, event_conversation.TurnFinished) == queued_turn


def assert_queued_attachment_turns(
    first: TranslationResult,
    queued: TranslationResult,
    stopped: TranslationResult,
    answer: TranslationResult,
) -> None:
    """Verify the queued attachment turn sequence."""
    queued_turn = turn_id_of(queued, event_conversation.TurnStarted)
    first_turn = payloads(first, event_conversation.TurnStarted)[0].turn_id
    assert_queued_turn_start(first_turn, queued_turn, queued)
    assert payloads(stopped, event_conversation.TurnFinished)[0].turn_id == queued_turn
    assert (
        payloads(answer, event_conversation.MessageCreated)[0].turn_id == queued_turn
    )
    assert (
        payloads(answer, event_conversation.TurnFinished)[0].turn_id == queued_turn
    )
