# Copyright (c) 2026 Zhambyl Yermagambet
"""Assertions for collaboration tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import (
    event_base,
    event_conversation,
    event_resource,
    ids as domain_ids,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_events import payloads
from tests.plugin_tests.support_values import text_of

if TYPE_CHECKING:
    from harness.models.raw_events import (
        TranslationResult,
    )


def assert_ignored_translation(translation: TranslationResult) -> None:
    """Check that translation explicitly ignored the record and produced no events."""
    assert translation.canonical_events == ()
    assert translation.decision == fixture.IGNORED_NONSEMANTIC


def turn_id_of(
    translation: TranslationResult,
    payload_type: type[event_base.EventPayload],
) -> domain_ids.TurnId | None:
    """Read the turn identity of the first event with the requested payload.

    Returns:
        The matching event's turn identity, which can be None.

    Raises:
        AssertionError: If no event has the requested payload type.

    """
    for event in translation.canonical_events:
        if isinstance(event.payload, payload_type):
            return event.turn_id
    message = f"translation has no {payload_type.__name__} event"
    raise AssertionError(message)


def assert_queued_turn_chain(
    first: TranslationResult,
    queued: TranslationResult,
    stopped: TranslationResult,
    answer: TranslationResult,
) -> None:
    """Verify that the queued turn continues through stop and answer."""
    queued_turn_id = turn_id_of(queued, event_conversation.TurnStarted)
    assert queued_turn_id is not None
    assert queued_turn_id != turn_id_of(first, event_conversation.TurnStarted)
    assert turn_id_of(stopped, event_conversation.TurnFinished) == queued_turn_id
    assert turn_id_of(answer, event_conversation.MessageCreated) == queued_turn_id
    assert turn_id_of(answer, event_conversation.TurnFinished) == queued_turn_id


def assert_web_search_result(answer: TranslationResult) -> None:
    """Verify one translated web search result."""
    performed = payloads(answer, event_resource.SearchPerformed)[0].payload
    assert performed.tool == fixture.WEB_SEARCH_NAME
    assert text_of(performed.query) == "Bali weather"
    assert text_of(performed.result) == "26C and sunny"


def assert_web_open_result(answer: TranslationResult) -> None:
    """Verify one translated web open result."""
    fetched = payloads(answer, event_resource.WebFetched)[0].payload
    assert fetched.url == fixture.HTTPS_EXAMPLE_COM_URL
    assert text_of(fetched.result) == fixture.EXAMPLE_DOMAIN_TEXT


def assert_failed_resource_read(answer: TranslationResult) -> None:
    """Verify one translated failed resource read."""
    accessed = payloads(answer, event_resource.FileAccessed)[0].payload
    assert accessed.path == "/work/missing.txt"
    assert accessed.action == "read"
    assert accessed.outcome == fixture.FAILED
