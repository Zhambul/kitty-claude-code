# Copyright (c) 2026 Zhambyl Yermagambet
"""Row shapes for the raw event and fact tables.

One frozen dataclass per table, fields named and ordered exactly as the columns
are, typed as SQLite sees them: `bytes` for BLOB, `int` for the 0/1 booleans,
`str` for the JSON columns. No methods, no defaults, no validation — the mapper
does all three.
"""

from __future__ import annotations

from dataclasses import dataclass

from domain import ids as domain_ids
from repository.model.session_data import (
    SessionDataActorRow as SessionDataActorRow,
    SessionDataRow as SessionDataRow,
    SessionEntryRow as SessionEntryRow,
    SessionRow as SessionRow,
)


@dataclass(frozen=True)
class RawEventRow:
    """Represent raw event row."""

    id: int
    raw_event_id: domain_ids.RawEventId
    session_id: domain_ids.SessionId
    harness: domain_ids.HarnessName
    source_type: str
    source_identity: str
    source_name: str
    source_position: str
    actor_id: domain_ids.ActorId
    parent_actor_id: domain_ids.ActorId | None
    observed_at: float
    encoding: str
    payload: bytes
    payload_codec: str
    terminal_window_id: domain_ids.WindowId | None
    harness_process_id: int | None
    account_id: domain_ids.AccountId | None
    account_display_name: str | None


@dataclass(frozen=True)
class CanonicalEventRow:
    """Represent canonical event row."""

    cursor: int
    event_id: domain_ids.CanonicalEventId
    schema_version: int
    event_type: str
    session_id: domain_ids.SessionId
    actor_id: domain_ids.ActorId
    turn_id: domain_ids.TurnId | None
    parent_actor_id: domain_ids.ActorId | None
    harness: domain_ids.HarnessName
    occurred_at: float | None
    terminal_window_id: domain_ids.WindowId | None
    harness_process_id: int | None
    accepted_at: float
    payload: str


@dataclass(frozen=True)
class ShellOutputRow:
    """Represent shell output row."""

    session_id: domain_ids.SessionId
    shell_id: domain_ids.ShellId
    harness: domain_ids.HarnessName
    actor_id: domain_ids.ActorId
    parent_actor_id: domain_ids.ActorId | None
    source_path: str
    chunk_source_type: str
    delete_source: int
    initial_size: int
    initial_modified_at: int
    wait_for_source_change: int
    until: str
    state: str
    created_at: float


@dataclass(frozen=True)
class SessionInsertRow:
    """Represent values for one session insert."""

    session_id: domain_ids.SessionId
    lead_actor_id: domain_ids.ActorId
    harness: domain_ids.HarnessName
    harness_session_id: domain_ids.SessionId
    source_reference: str
    working_directory: str | None
    project_directory: str | None
    terminal_window_id: domain_ids.WindowId | None
    harness_process_id: int | None
    created_at: float


@dataclass(frozen=True)
class RawEventInsertRow:
    """Represent values for one raw-event insert."""

    raw_event_id: domain_ids.RawEventId
    session_id: domain_ids.SessionId
    harness: domain_ids.HarnessName
    source_type: str
    source_identity: str
    source_name: str
    source_position: str
    actor_id: domain_ids.ActorId
    parent_actor_id: domain_ids.ActorId | None
    observed_at: float
    encoding: str
    payload: bytes
    payload_codec: str
    terminal_window_id: domain_ids.WindowId | None
    harness_process_id: int | None
    account_id: domain_ids.AccountId | None
    account_display_name: str | None


@dataclass(frozen=True)
class RawEventIdentity:
    """Represent the columns that define one raw-event identity."""

    session_id: domain_ids.SessionId
    harness: domain_ids.HarnessName
    source_type: str
    source_name: str
    source_position: str
    actor_id: domain_ids.ActorId
    parent_actor_id: domain_ids.ActorId | None
    encoding: str
    payload: bytes


@dataclass(frozen=True)
class CanonicalEventInsertRow:
    """Represent values for one canonical-event insert."""

    event_id: domain_ids.CanonicalEventId
    schema_version: int
    event_type: str
    session_id: domain_ids.SessionId
    actor_id: domain_ids.ActorId
    turn_id: domain_ids.TurnId | None
    parent_actor_id: domain_ids.ActorId | None
    harness: domain_ids.HarnessName
    occurred_at: float | None
    terminal_window_id: domain_ids.WindowId | None
    harness_process_id: int | None
    accepted_at: float
    payload: str
