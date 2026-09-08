# Copyright (c) 2026 Zhambyl Yermagambet
"""Recording dependencies for the frontend fixture seed."""

from domain import composer as composer, event_base as event_base, records as domain_records
from harness.models.raw_events import RawEvent as RawEvent, TranslationResult as TranslationResult
from harness.models.session import Session as Session


def translated(fact: event_base.CanonicalEvent[event_base.EventPayload]) -> TranslationResult:
    """Return a translated fixture fact.

    Returns:
        A translated fixture fact.

    """
    return TranslationResult((fact,), domain_records.RecordedTranslationDecision.TRANSLATED)
