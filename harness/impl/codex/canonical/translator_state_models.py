# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from dataclasses import dataclass

from harness.impl.codex.canonical import translator_dependencies as dependencies


@dataclass(frozen=True)
class RecordSource:
    """Hold a raw record and the identity used for its translation."""

    raw_event: dependencies.translator_service_dependencies.raw_events.RawEvent
    source_key: str
    native_payload: dependencies.record_payload_namespaces.record_rollout_headers.NativePayloadIdentity | None
    native_identity: str
    occurred_at: float | None


@dataclass(frozen=True)
class ConversationSemantics:
    """Hold the role, phase, and turn of a conversation record."""

    role: dependencies.translator_domain_values.messaging.MessageRole
    phase: dependencies.translator_domain_values.messaging.MessagePhase | None
    turn_id: dependencies.translator_type_dependencies.ids.TurnId | None


@dataclass(frozen=True)
class ShellProcess:
    """Hold a native shell result and its process identity."""

    exit_code: int | None
    process_id: dependencies.translator_id_dependencies.ids_session_types.CodexShellId
    yielded_with_identity: bool


@dataclass(frozen=True)
class ShellResultContext:
    """Link a shell result to its source, shell, and turn."""

    source: RecordSource
    source_key: str
    shell_id: dependencies.translator_type_dependencies.ids.ShellId
    turn_id: dependencies.translator_type_dependencies.ids.TurnId | None


@dataclass(frozen=True)
class CommandCompletion:
    """Link a completed command record to its source and turn."""

    source: RecordSource
    record: dependencies.record_canonical_namespaces.record_tool_records.CommandCompletedRecord
    source_key: str
    turn_id: dependencies.translator_type_dependencies.ids.TurnId | None


@dataclass(frozen=True)
class ResolvedCompletedShell:
    """Hold a completed shell identity and an optional start event."""

    shell_id: dependencies.translator_type_dependencies.ids.ShellId
    started: (
        dependencies.translator_type_dependencies.event_base.CanonicalEvent[
            dependencies.translator_type_dependencies.event_base.EventPayload
        ]
        | None
    )
