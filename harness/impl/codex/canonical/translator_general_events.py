# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import (
    COMPLETED_STATUS,
    FILE_ACTIONS,
    FILE_SUBJECT,
)

if TYPE_CHECKING:
    from harness.impl.codex.canonical.translator_state_models import RecordSource


def mcp_outcome(status: str) -> dependencies.translator_domain_values.outcomes.Outcome:
    """Convert a completed MCP tool status to a canonical outcome.

    Returns:
        The failed or successful outcome.

    Raises:
        TranslationError: If the completion status is not recognized.

    """
    if status == "failed":
        return dependencies.translator_domain_values.outcomes.Outcome.FAILED
    if status == COMPLETED_STATUS:
        return dependencies.translator_domain_values.outcomes.Outcome.SUCCEEDED
    msg = f"unknown Codex MCP completion state: {status!r}"
    raise dependencies.translator_service_dependencies.raw_events.TranslationError(
        msg,
    )


def search_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_tool_records.SearchRecord,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build an event for a completed web search.

    Returns:
        The search event with its query and source time.

    """
    payload = dependencies.translator_domain_events.event_resource.SearchPerformed(
        "web_search",
        dependencies.translator_codex_dependencies.support.content(record.query),
        None,
        dependencies.translator_domain_values.outcomes.Outcome.SUCCEEDED,
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "search",
            record_source.native_identity,
            "performed",
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )


def patch_events(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_context_records.PatchRecord,
) -> list[
    dependencies.translator_type_dependencies.event_base.CanonicalEvent[
        dependencies.translator_type_dependencies.event_base.EventPayload
    ]
]:
    """Build file events from a patch record.

    Returns:
        One event per file, in the order supplied by the patch.

    """
    outcome = dependencies.translator_codex_dependencies.support.outcome_of(succeeded=record.success)
    return [
        _patch_event(record_source, file_order, file_record, outcome)
        for file_order, file_record in enumerate(record.files)
    ]


def _patch_event(
    record_source: RecordSource,
    file_order: int,
    file_record: dependencies.record_canonical_namespaces.record_context_records.PatchFile,
    outcome: dependencies.translator_domain_values.outcomes.Outcome,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    payload = dependencies.translator_domain_events.event_resource.FileAccessed(
        path=file_record.path,
        action=FILE_ACTIONS.get(
            file_record.change or "",
            dependencies.translator_domain_values.outcomes.FileAction.UPDATED,
        ),
        outcome=outcome,
        previous_path=file_record.previous_path,
        lines_added=file_record.added,
        lines_removed=file_record.removed,
        unified_diff=file_record.diff,
        content=None
        if file_record.content is None
        else dependencies.translator_codex_dependencies.support.content(file_record.content),
    )
    identity = f"{record_source.native_identity}:{file_order}:{file_record.path}"
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            FILE_SUBJECT,
            identity,
            "accessed",
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )


def usage_events(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_context_records.UsageRecord,
) -> list[
    dependencies.translator_type_dependencies.event_base.CanonicalEvent[
        dependencies.translator_type_dependencies.event_base.EventPayload
    ]
]:
    """Build token usage events from a native usage record.

    Returns:
        The session usage event and, when available, its context usage event.

    """
    events = [_usage_event(record_source, record)]
    if record.last is not None and record.window:
        events.append(_context_event(record_source, record))
    return events


def _usage_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_context_records.UsageRecord,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    tokens = dependencies.translator_domain_values.usage.TokenUsage(
        input_tokens=record.usage.input_tokens or 0,
        output_tokens=record.usage.output_tokens or 0,
        cache_read_tokens=record.usage.cached_input_tokens or 0,
    )
    payload = dependencies.translator_domain_values.event_telemetry.UsageReported(
        scope=dependencies.translator_domain_values.usage.UsageScope.SESSION,
        subject_id=str(record_source.raw_event.session_id),
        model=None,
        account=None,
        tokens=tokens,
        cumulative=True,
        cost_in_usd=None,
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "usage",
            record_source.native_identity,
            "reported",
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )


def _context_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_context_records.UsageRecord,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    if record.last is None or record.window is None:
        msg = "Codex context usage is incomplete"
        raise dependencies.translator_service_dependencies.raw_events.TranslationError(
            msg,
        )
    context_reported = dependencies.translator_domain_values.event_telemetry.ContextReported
    payload = context_reported(record.last.total_tokens or 0, record.window, None)
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "context",
            record_source.native_identity,
            "reported",
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )
