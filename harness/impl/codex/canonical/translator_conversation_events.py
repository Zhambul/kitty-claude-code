# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import (
    FINISHED_PHASE,
    SKILL_SUBJECT,
    STARTED_PHASE,
)
from harness.impl.codex.canonical.translator_state_models import (
    ConversationSemantics,
    RecordSource,
)


def cancelled_child_assignment(
    record_source: RecordSource,
    native_turn_id: dependencies.translator_id_dependencies.ids_conversation_types.CodexTurnId,
    turn_id: dependencies.translator_type_dependencies.ids.TurnId,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build the assignment finish for an interrupted child turn.

    Returns:
        The cancelled assignment event with an interruption reason.

    """
    assignment_id = dependencies.translator_id_dependencies.ids_conversation.assignment_id_from_codex_turn(
        native_turn_id,
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "actor_assignment",
            str(assignment_id),
            FINISHED_PHASE,
            dependencies.translator_domain_events.event_actor.ActorAssignmentFinished(
                assignment_id, dependencies.translator_domain_values.outcomes.Outcome.CANCELLED, None, "interrupted",
            ),
            turn_id=turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )


def conversation_event(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_task_records.PromptRecord
    | dependencies.record_canonical_namespaces.record_task_records.MessageRecord
    | dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a message event from a prompt, message, or chat record.

    Returns:
        The message with its canonical role, phase, and turn identifier.

    """
    semantics = _conversation_semantics(record)
    message_id = dependencies.translator_id_dependencies.ids_conversation.message_id_from_codex(
        dependencies.translator_id_dependencies.ids_conversation_types.CodexMessageId(record_source.native_identity),
    )
    payload: dependencies.translator_type_dependencies.event_base.EventPayload = (
        dependencies.translator_domain_events.event_conversation.MessageCreated(
            message_id,
            semantics.role,
            dependencies.translator_codex_dependencies.support.content(
                record.text,
                markdown=semantics.role == dependencies.translator_domain_values.messaging.MessageRole.ASSISTANT,
            ),
            semantics.phase,
            None,
        )
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "message",
            str(message_id),
            "created",
            payload,
            turn_id=semantics.turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )


def _conversation_semantics(
    record: dependencies.record_canonical_namespaces.record_task_records.PromptRecord
    | dependencies.record_canonical_namespaces.record_task_records.MessageRecord
    | dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord,
) -> ConversationSemantics:
    role = (
        dependencies.translator_domain_values.messaging.MessageRole.USER
        if isinstance(record, dependencies.record_canonical_namespaces.record_task_records.PromptRecord)
        else dependencies.translator_domain_values.messaging.MessageRole.ASSISTANT
    )
    if isinstance(record, dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord):
        role = _chat_role(record.role)
    synthetic = (
        record.synthetic
        if isinstance(record, dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord)
        else False
    )
    if synthetic:
        role = dependencies.translator_domain_values.messaging.MessageRole.SYSTEM
    phase = _conversation_phase(record, role, synthetic=synthetic)
    turn_id = _conversation_turn_id(record)
    return ConversationSemantics(role, phase, turn_id)


def _conversation_turn_id(
    record: dependencies.record_canonical_namespaces.record_task_records.PromptRecord
    | dependencies.record_canonical_namespaces.record_task_records.MessageRecord
    | dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord,
) -> dependencies.translator_type_dependencies.ids.TurnId | None:
    if (
        isinstance(record, dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord)
        and record.turn
    ):
        return dependencies.translator_id_dependencies.ids_conversation.turn_id_from_codex(
            dependencies.translator_id_dependencies.ids_conversation_types.CodexTurnId(record.turn),
        )
    return None


def _chat_role(native_role: str) -> dependencies.translator_domain_values.messaging.MessageRole:
    if native_role == "user":
        return dependencies.translator_domain_values.messaging.MessageRole.USER
    if native_role == "system":
        return dependencies.translator_domain_values.messaging.MessageRole.SYSTEM
    return dependencies.translator_domain_values.messaging.MessageRole.ASSISTANT


def _conversation_phase(
    record: dependencies.record_canonical_namespaces.record_task_records.PromptRecord
    | dependencies.record_canonical_namespaces.record_task_records.MessageRecord
    | dependencies.record_canonical_namespaces.record_interaction_records.ChatRecord,
    role: dependencies.translator_domain_values.messaging.MessageRole,
    *,
    synthetic: bool,
) -> dependencies.translator_domain_values.messaging.MessagePhase | None:
    if synthetic:
        return dependencies.translator_domain_values.messaging.MessagePhase.SYNTHETIC
    if (
        isinstance(record, dependencies.record_canonical_namespaces.record_task_records.PromptRecord)
        or role == dependencies.translator_domain_values.messaging.MessageRole.USER
    ):
        return dependencies.translator_domain_values.messaging.MessagePhase.PROMPT
    if record.phase == dependencies.translator_codex_dependencies.PHASE_FINAL:
        return dependencies.translator_domain_values.messaging.MessagePhase.END_TURN
    if role == dependencies.translator_domain_values.messaging.MessageRole.ASSISTANT:
        return dependencies.translator_domain_values.messaging.MessagePhase.INTERMEDIATE
    return None


def skill_events(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_task_records.SkillRecord,
) -> list[
    dependencies.translator_type_dependencies.event_base.CanonicalEvent[
        dependencies.translator_type_dependencies.event_base.EventPayload
    ]
]:
    """Build the start and finish events for a completed native skill.

    Returns:
        The skill start followed by its successful finish and output.

    """
    skill_id = dependencies.translator_id_dependencies.ids_work.skill_id_from_codex(
        dependencies.translator_id_dependencies.ids_work_types.CodexSkillId(record_source.native_identity),
    )
    turn_id = (
        dependencies.translator_id_dependencies.ids_conversation.turn_id_from_codex(
            dependencies.translator_id_dependencies.ids_conversation_types.CodexTurnId(record.turn),
        )
        if record.turn
        else None
    )
    return [
        dependencies.translator_codex_dependencies.support.event(
            record_source.raw_event,
            dependencies.translator_service_dependencies.CanonicalEventDraft(
                SKILL_SUBJECT,
                record_source.native_identity,
                STARTED_PHASE,
                dependencies.translator_domain_events.event_resource.SkillStarted(skill_id, record.name, None),
                turn_id=turn_id,
                occurred_at=record_source.occurred_at,
            ),
        ),
        dependencies.translator_codex_dependencies.support.event(
            record_source.raw_event,
            dependencies.translator_service_dependencies.CanonicalEventDraft(
                SKILL_SUBJECT,
                record_source.native_identity,
                FINISHED_PHASE,
                dependencies.translator_domain_events.event_resource.SkillFinished(
                    skill_id,
                    dependencies.translator_domain_values.outcomes.Outcome.SUCCEEDED,
                    dependencies.translator_codex_dependencies.support.content(record.output),
                ),
                turn_id=turn_id,
                occurred_at=record_source.occurred_at,
            ),
        ),
    ]
