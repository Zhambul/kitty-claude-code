# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed operational raw events reported by dashboard clients."""

from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Protocol

from audit.documents import AuditDocument
from audit.records import StateFileRecord
from domain.ids import ClientId, DeviceId, SessionId
from repository.mapper import audit as mapper

Scalar = str | int | float | bool | None


class StateFileWriter(Protocol):
    """Store an audited state-file record."""

    def record_state_file(self, state_file_record: StateFileRecord) -> None:
        """Record a state-file operation."""
        ...


class OptimisticActionReport(AuditDocument):
    """Describe one optimistic browser action."""

    session_id: SessionId
    action: str
    phase: str
    character_count: int | None
    elapsed_milliseconds: int | None
    reason: str | None


class ClientFailureReport(AuditDocument):
    """Describe one client action failure."""

    session_id: SessionId
    gesture: str
    failure_kind: str
    error: str | None
    status_code: int | None
    character_count: int | None


class BrowserEvent(AuditDocument):
    """Describe one event from a browser client."""

    session_id: SessionId | None
    name: str
    timestamp: int | None
    details: Mapping[str, Scalar]


class BrowserEventBatch(AuditDocument):
    """Hold browser events that share connection details."""

    client_id: ClientId
    device_id: DeviceId
    connection: Mapping[str, Scalar]
    events: tuple[BrowserEvent, ...]


class BrowserEventAudit(AuditDocument):
    """Describe one browser event for audit storage."""

    client_id: ClientId
    device_id: DeviceId
    session_id: SessionId | None
    name: str
    details: Mapping[str, Scalar]
    connection: Mapping[str, Scalar]
    timestamp: int | None


class BrowserTelemetryService:
    """Write browser-only observations to the operational audit."""

    def __init__(self, state_file_writer: StateFileWriter, process_id: int = 0) -> None:
        """Create a service with a repository and a process identifier."""
        self.audit_write_repository = state_file_writer
        self.process_id = process_id

    def record_optimistic_action(self, optimistic_action_report: OptimisticActionReport) -> None:
        """Record one optimistic browser action."""
        self._record("browser-optimistic-action", optimistic_action_report)

    def record_client_failure(self, client_failure_report: ClientFailureReport) -> None:
        """Record one browser client failure."""
        self._record("browser-client-failure", client_failure_report)

    def record_events(self, browser_event_batch: BrowserEventBatch) -> None:
        """Record all events in one browser event batch."""
        for event in browser_event_batch.events:
            self._record(
                "browser-event",
                BrowserEventAudit(
                    client_id=browser_event_batch.client_id,
                    device_id=browser_event_batch.device_id,
                    session_id=event.session_id,
                    name=event.name,
                    details=event.details,
                    connection=browser_event_batch.connection,
                    timestamp=event.timestamp,
                ),
            )

    def _record(self, action: str, audit_document: AuditDocument) -> None:
        self.audit_write_repository.record_state_file(
            StateFileRecord(
                session_id=SessionId(""),
                path="",
                action=action,
                content=mapper.truncated(audit_document),
                script="dashboard",
                process_id=self.process_id,
                timestamp=time.time(),
            ),
        )
