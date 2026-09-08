# Copyright (c) 2026 Zhambyl Yermagambet
"""Validate canonical events against the raw event that produced them."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.records import RecordedTranslationDecision
from harness.models.raw_events import (
    RawEvent,
    TranslationResult,
)

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload


class TranslationConsistencyError(ValueError):
    """Report canonical output that conflicts with its raw event."""


def checked(raw_event: RawEvent, translation_result: TranslationResult) -> TranslationResult:
    """Return a failed verdict when canonical output is inconsistent.

    Returns:
        A failed verdict when canonical output is inconsistent.

    """
    try:
        for canonical_event in translation_result.canonical_events:
            _check_consistency(raw_event, canonical_event)
    except TranslationConsistencyError as error:
        reason = f"inconsistent canonical output: {error}"
        return TranslationResult((), RecordedTranslationDecision.TRANSLATION_FAILED, reason)
    return translation_result


def _check_consistency(raw_event: RawEvent, canonical_event: CanonicalEvent[EventPayload]) -> None:
    inconsistency = _inconsistency(raw_event, canonical_event)
    if inconsistency is not None:
        raise TranslationConsistencyError(inconsistency)


def _inconsistency(raw_event: RawEvent, canonical_event: CanonicalEvent[EventPayload]) -> str | None:
    """Return the first inconsistency between a raw and canonical event.

    Returns:
        The first inconsistency between a raw and canonical event.

    """
    identity_inconsistency = _identity_inconsistency(raw_event, canonical_event)
    if identity_inconsistency is not None:
        return identity_inconsistency
    if canonical_event.parent_actor_id == canonical_event.actor_id:
        return "an actor cannot be its own parent"
    return None


def _identity_inconsistency(raw_event: RawEvent, canonical_event: CanonicalEvent[EventPayload]) -> str | None:
    """Return the first raw-event identity mismatch.

    Returns:
        The first raw-event identity mismatch.

    """
    if canonical_event.session_id != raw_event.session_id:
        return "canonical event does not belong to its raw event session"
    if canonical_event.harness != raw_event.harness:
        return "canonical event harness does not match its raw event"
    if canonical_event.actor_id != raw_event.actor_id:
        return "canonical event actor does not match its raw event"
    if canonical_event.parent_actor_id != raw_event.parent_actor_id:
        return "canonical event parent actor does not match its raw event"
    return None
