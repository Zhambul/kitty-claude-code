# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared value coercion and canonical event construction for Codex translation."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from domain.content import Content, MediaType, TextContent
from domain.outcomes import Outcome
from domain.references import ModelReference
from harness.models.raw_event_builders import CanonicalEventDraft as CanonicalEventDraft, canonical_event

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.impl.codex.model import CodexModel
    from harness.models.raw_events import RawEvent


def model_reference(codex_model: CodexModel) -> ModelReference:
    """Return the model reference.

    Returns:
        Model reference.

    """
    return ModelReference(codex_model, codex_model)


def timestamp(timestamp_source: str | float | None) -> float | None:
    """Return the timestamp.

    Returns:
        Timestamp.

    """
    if isinstance(timestamp_source, (int, float)):
        return float(timestamp_source)
    if not timestamp_source:
        return None
    try:
        return datetime.fromisoformat(timestamp_source).timestamp()
    except ValueError:
        return None


def exit_code(status_source: str | int | None) -> int | None:
    """Return the exit code.

    A record's exit status, honest about zero: `0` is a real exit code
        (a falsy-int coercion once turned a clean exit into outcome "failed").

    Returns:
        Exit code.

    """
    # Parsed from the same string the guard tests, rather than from the raw
    # value: the two were separate expressions, so nothing connected "this
    # renders as digits" to "this converts to an int".
    text = str(status_source)
    return int(text) if text.lstrip("-").isdigit() else None


def content(content_source: str | None, *, markdown: bool = False) -> Content:
    """Return the content.

    Returns:
        Content.

    """
    return TextContent(content_source or "", MediaType.TEXT_MARKDOWN if markdown else MediaType.TEXT_PLAIN)


def event(
    raw_event: RawEvent,
    canonical_event_draft: CanonicalEventDraft,
) -> CanonicalEvent[EventPayload]:
    """Return the event.

    Returns:
        Event.

    """
    return canonical_event(raw_event, canonical_event_draft)


def outcome_of(*, succeeded: bool) -> Outcome:
    """Return the outcome of.

    Returns:
        Outcome of.

    """
    return Outcome.SUCCEEDED if succeeded else Outcome.FAILED
