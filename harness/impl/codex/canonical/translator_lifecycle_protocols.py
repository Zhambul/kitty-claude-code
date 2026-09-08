# Copyright (c) 2026 Zhambyl Yermagambet
"""Define late-stage Codex translator interfaces."""

from typing import Protocol

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_state_models import RecordSource, ShellProcess, ShellResultContext


class RecordTranslator(Protocol):
    """Translate one parsed rollout record."""

    def _translate_record(
        self,
        raw_event: dependencies.translator_service_dependencies.raw_events.RawEvent,
        rollout_observation: dependencies.record_payload_namespaces.record_rollout_headers.RolloutObservation,
        record: dependencies.record_canonical_namespaces.record_terminal_records.RolloutRecord,
    ) -> list[
        dependencies.translator_type_dependencies.event_base.CanonicalEvent[
            dependencies.translator_type_dependencies.event_base.EventPayload
        ]
    ]: ...


class RecordTailTranslator(Protocol):
    """Translate a completed non-shell tool call."""

    def _exec_result_events(
        self,
        record_source: RecordSource,
        record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
    ) -> list[
        dependencies.translator_type_dependencies.event_base.CanonicalEvent[
            dependencies.translator_type_dependencies.event_base.EventPayload
        ]
    ]: ...

    def _tool_result(
        self,
        raw_event: dependencies.translator_service_dependencies.raw_events.RawEvent,
        call_id: dependencies.translator_id_dependencies.ids_session_types.CodexCallId,
        tool_record: dependencies.record_canonical_namespaces.record_tool_records.ToolRecord,
        exec_result_record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
        occurred_at: float | None,
    ) -> list[
        dependencies.translator_type_dependencies.event_base.CanonicalEvent[
            dependencies.translator_type_dependencies.event_base.EventPayload
        ]
    ]: ...


class ShellResultTranslator(Protocol):
    """Translate a completed shell result."""

    def _finished_shell_result(
        self,
        shell_result_context: ShellResultContext,
        shell_process: ShellProcess,
        record: dependencies.record_canonical_namespaces.record_tool_records.ExecResultRecord,
    ) -> list[
        dependencies.translator_type_dependencies.event_base.CanonicalEvent[
            dependencies.translator_type_dependencies.event_base.EventPayload
        ]
    ]: ...
