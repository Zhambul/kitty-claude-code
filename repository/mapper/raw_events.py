# Copyright (c) 2026 Zhambyl Yermagambet
"""Map stored raw-event rows to raw-event models."""

from __future__ import annotations

from domain import ids as domain_ids
from harness.models import raw_events as raw_event_models
from repository.mapper import raw_payloads
from repository.model.facts import RawEventIdentity, RawEventInsertRow, RawEventRow


def raw_event(raw_event_row: RawEventRow) -> raw_event_models.RawEvent:
    """Return the raw event model for a stored row.

    Returns:
        The raw event model for a stored row.

    """
    return raw_event_models.RawEvent(
        raw_event_id=domain_ids.RawEventId(raw_event_row.raw_event_id),
        harness=domain_ids.HarnessName(raw_event_row.harness),
        source_type=raw_event_row.source_type,
        source_name=raw_event_row.source_name,
        source_position=raw_event_row.source_position,
        session_id=domain_ids.SessionId(raw_event_row.session_id),
        actor_id=domain_ids.ActorId(raw_event_row.actor_id),
        parent_actor_id=(
            None if raw_event_row.parent_actor_id is None else domain_ids.ActorId(raw_event_row.parent_actor_id)
        ),
        observed_at=raw_event_row.observed_at,
        encoding=raw_event_row.encoding,
        payload=raw_payloads.restored(raw_event_row.payload, raw_event_row.payload_codec),
        source_identity=raw_event_row.source_identity,
        terminal_window_id=raw_event_row.terminal_window_id,
        harness_process_id=raw_event_row.harness_process_id,
        account_id=raw_event_row.account_id,
        account_display_name=raw_event_row.account_display_name,
    )


def raw_event_insert_row(raw_event: raw_event_models.RawEvent) -> RawEventInsertRow:
    """Return the storage row for a raw event model.

    Returns:
        The storage row for a raw event model.

    """
    stored_payload, payload_codec = raw_payloads.stored(raw_event.payload)
    return RawEventInsertRow(
        raw_event_id=raw_event.raw_event_id,
        session_id=raw_event.session_id,
        harness=raw_event.harness,
        source_type=raw_event.source_type,
        source_identity=raw_event.source_identity or raw_event.source_type,
        source_name=raw_event.source_name,
        source_position=raw_event.source_position,
        actor_id=raw_event.actor_id,
        parent_actor_id=raw_event.parent_actor_id,
        observed_at=raw_event.observed_at,
        encoding=raw_event.encoding,
        payload=stored_payload,
        payload_codec=payload_codec,
        terminal_window_id=raw_event.terminal_window_id,
        harness_process_id=raw_event.harness_process_id,
        account_id=raw_event.account_id,
        account_display_name=raw_event.account_display_name,
    )


def raw_event_identity(raw_event: raw_event_models.RawEvent) -> RawEventIdentity:
    """Return the identity values for a raw event model.

    Returns:
        The identity values for a raw event model.

    """
    return RawEventIdentity(
        session_id=raw_event.session_id,
        harness=raw_event.harness,
        source_type=raw_event.source_type,
        source_name=raw_event.source_name,
        source_position=raw_event.source_position,
        actor_id=raw_event.actor_id,
        parent_actor_id=raw_event.parent_actor_id,
        encoding=raw_event.encoding,
        payload=raw_event.payload,
    )
