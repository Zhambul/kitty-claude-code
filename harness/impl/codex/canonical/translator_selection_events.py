# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import (
    CHANGED_PHASE,
    GOAL_STATES,
    MISSING_NATIVE_VALUE,
)
from harness.impl.codex.canonical.translator_recovery import _PendingExecRecovery

if TYPE_CHECKING:
    from harness.impl.codex.canonical.translator_state_models import RecordSource


def selection_event(
    record_source: RecordSource,
    subject: str,
    payload: dependencies.translator_type_dependencies.event_base.EventPayload,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a model or effort change from its source record.

    Returns:
        The canonical event with the source identity and time.

    """
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            subject,
            record_source.native_identity,
            CHANGED_PHASE,
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )


def attention_prompts(
    record: dependencies.record_canonical_namespaces.record_interaction_records.AskRecord,
) -> tuple[dependencies.translator_domain_events.attention.AttentionPrompt, ...]:
    """Convert native questions and options to attention prompts.

    Returns:
        The prompts in their native order.

    """
    return tuple(
        dependencies.translator_domain_events.attention.AttentionPrompt(
            prompt_id=dependencies.translator_id_dependencies.ids_conversation.question_id_from_codex(
                dependencies.translator_id_dependencies.ids_conversation_types.CodexQuestionId(
                    question.id or str(index),
                ),
            ),
            title=question.header or None,
            prompt=question.question or "",
            multiple=False,
            choices=tuple(
                dependencies.translator_domain_events.attention.AttentionChoice(option.label, option.description)
                for option in question.options
            ),
        )
        for index, question in enumerate(record.questions)
    )


def plan_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_interaction_records.PlanRecord,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a proposed plan from its native record.

    Returns:
        The plan event with its attention identifier and content.

    """
    attention_id = dependencies.translator_id_dependencies.ids_attention.attention_id_from_codex(
        dependencies.translator_id_dependencies.ids_conversation_types.CodexAttentionId(
            record.id or record_source.native_identity,
        ),
    )
    content = dependencies.translator_codex_dependencies.support.content(record.text or "", markdown=True)
    payload = dependencies.translator_domain_values.event_work.PlanProposed(attention_id, content)
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "plan",
            str(attention_id),
            "proposed",
            payload,
            occurred_at=record_source.occurred_at,
        ),
    )


def goal_state(native_state: str) -> dependencies.translator_domain_values.work_state.GoalState:
    """Map a native goal state to its canonical value.

    Returns:
        The canonical goal state.

    Raises:
        TranslationError: If the native state is not known.

    """
    state = GOAL_STATES.get(native_state)
    if state is None:
        reported_state = native_state or MISSING_NATIVE_VALUE
        message = f"unknown Codex goal state: {reported_state}"
        raise dependencies.translator_service_dependencies.raw_events.TranslationError(message)
    return state


def goal_reason(reason_text: str | None) -> str | None:
    """Return a normalized optional goal reason.

    Returns:
        A normalized optional goal reason.

    """
    if reason_text is None:
        return None
    normalized = reason_text.strip()
    return normalized or None


def recover_pending_exec(
    source_path: str,
    end_position: int,
    command_texts: set[str],
) -> dependencies.record_canonical_namespaces.record_tool_records.ExecRecord | None:
    """Find the first pending command before a source byte position.

    Returns:
        The matching pending call, or None if no call can be recovered.

    """
    recovery = _PendingExecRecovery(command_texts, [])
    try:
        with pathlib.Path(source_path).open("rb") as source:
            recovery.read(source, end_position)
    except OSError:
        return None
    return recovery.pending[0] if recovery.pending else None


def decoded_rollout(raw_event: dependencies.translator_service_dependencies.raw_events.RawEvent) -> str:
    """Decode the text of a native rollout record.

    Returns:
        The record text.

    Raises:
        TranslationError: If the payload is not valid UTF-8.

    """
    try:
        return raw_event.payload.decode("utf-8")
    except UnicodeDecodeError as error:
        msg = "malformed Codex rollout record"
        raise dependencies.translator_service_dependencies.raw_events.TranslationError(
            msg, context=raw_event.source_position,
        ) from error
