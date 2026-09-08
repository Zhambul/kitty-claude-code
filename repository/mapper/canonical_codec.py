# Copyright (c) 2026 Zhambyl Yermagambet
"""Validate and encode canonical event payloads."""

from __future__ import annotations

from functools import cache
from typing import Any, cast

from pydantic import TypeAdapter, ValidationError

from domain import event_base, events as domain_events
from repository.mapper.documents import StoredDocumentError


def event_type(event_payload: event_base.EventPayload) -> str:
    """Return the registered canonical event type.

    Returns:
        The registered canonical event type.

    Raises:
        StoredDocumentError: If the payload class is not registered.

    """
    try:
        return domain_events.EVENT_TYPES[type(event_payload)]
    except KeyError as error:
        msg = f"unregistered canonical payload: {type(event_payload).__name__}"
        raise StoredDocumentError(msg) from error


@cache
def event_adapter(event_type_name: str) -> TypeAdapter[Any]:
    """Return the validator for one canonical event type.

    Returns:
        The validator for one canonical event type.

    """
    event = cast("Any", event_base.CanonicalEvent)
    return TypeAdapter(event[domain_events.PAYLOAD_TYPES[event_type_name]])


@cache
def payload_adapter(event_type_name: str) -> TypeAdapter[Any]:
    """Return the codec for one canonical payload type.

    Returns:
        The codec for one canonical payload type.

    """
    return TypeAdapter(domain_events.PAYLOAD_TYPES[event_type_name])


def validated(canonical_event: event_base.CanonicalEvent[event_base.EventPayload]) -> str:
    """Validate a canonical event.

    Returns:
        The registered event type name.

    Raises:
        StoredDocumentError: If the event does not match its registered schema.

    """
    event_type_name = event_type(canonical_event.payload)
    try:
        event_adapter(event_type_name).validate_python(canonical_event)
    except ValidationError as error:
        msg = f"invalid canonical event: {error}"
        raise StoredDocumentError(msg) from error
    return event_type_name


def payload_json(canonical_event: event_base.CanonicalEvent[event_base.EventPayload]) -> str:
    """Return the JSON payload for a canonical event.

    Returns:
        The JSON payload for a canonical event.

    """
    adapter = payload_adapter(event_type(canonical_event.payload))
    return adapter.dump_json(canonical_event.payload).decode("utf-8")


def payload(event_type_name: str, encoded_payload: str) -> event_base.EventPayload:
    """Return the decoded canonical payload.

    Returns:
        The decoded canonical payload.

    Raises:
        StoredDocumentError: If the event type is unknown or the payload is invalid.

    """
    if event_type_name not in domain_events.PAYLOAD_TYPES:
        msg = f"unknown canonical event type: {event_type_name!r}"
        raise StoredDocumentError(msg)
    try:
        decoded: event_base.EventPayload = payload_adapter(event_type_name).validate_json(encoded_payload)
    except ValidationError as error:
        msg = f"invalid canonical payload: {error}"
        raise StoredDocumentError(msg) from error
    return decoded
