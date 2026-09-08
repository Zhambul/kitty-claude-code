# Copyright (c) 2026 Zhambyl Yermagambet
"""Map canonical events to and from storage rows."""

from __future__ import annotations

from domain import event_base, events as domain_events, ids as domain_ids
from repository.mapper import canonical_codec
from repository.mapper.documents import StoredDocumentError
from repository.model.facts import CanonicalEventInsertRow, CanonicalEventRow


def canonical_event_insert_row(
    canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
    accepted_at: float,
) -> CanonicalEventInsertRow:
    """Return the storage row for a canonical event.

    Returns:
        The storage row for a canonical event.

    """
    event_type_name = canonical_codec.validated(canonical_event)
    return CanonicalEventInsertRow(
        event_id=canonical_event.event_id,
        schema_version=domain_events.SCHEMA_VERSION,
        event_type=event_type_name,
        session_id=canonical_event.session_id,
        actor_id=canonical_event.actor_id,
        turn_id=canonical_event.turn_id,
        parent_actor_id=canonical_event.parent_actor_id,
        harness=canonical_event.harness,
        occurred_at=canonical_event.occurred_at,
        terminal_window_id=canonical_event.terminal_window_id,
        harness_process_id=canonical_event.harness_process_id,
        accepted_at=accepted_at,
        payload=canonical_codec.payload_json(canonical_event),
    )


def row_canonical_event(
    canonical_event_row: CanonicalEventRow,
    raw_event_ids: tuple[domain_ids.RawEventId, ...] = (),
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Return the canonical event for a storage row.

    Returns:
        The canonical event for a storage row.

    Raises:
        StoredDocumentError: If the stored schema version is not supported.

    """
    if canonical_event_row.schema_version != domain_events.SCHEMA_VERSION:
        msg = f"unsupported canonical schema version: {canonical_event_row.schema_version!r}"
        raise StoredDocumentError(msg)
    return event_base.CanonicalEvent(
        event_id=domain_ids.CanonicalEventId(canonical_event_row.event_id),
        session_id=domain_ids.SessionId(canonical_event_row.session_id),
        actor_id=domain_ids.ActorId(canonical_event_row.actor_id),
        turn_id=(None if canonical_event_row.turn_id is None else domain_ids.TurnId(canonical_event_row.turn_id)),
        parent_actor_id=(
            None
            if canonical_event_row.parent_actor_id is None
            else domain_ids.ActorId(canonical_event_row.parent_actor_id)
        ),
        harness=domain_ids.HarnessName(canonical_event_row.harness),
        occurred_at=canonical_event_row.occurred_at,
        terminal_window_id=canonical_event_row.terminal_window_id,
        harness_process_id=canonical_event_row.harness_process_id,
        payload=canonical_codec.payload(canonical_event_row.event_type, canonical_event_row.payload),
        cursor=canonical_event_row.cursor,
        accepted_at=canonical_event_row.accepted_at,
        raw_event_ids=raw_event_ids,
    )
