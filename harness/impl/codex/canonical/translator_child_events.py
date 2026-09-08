# Copyright (c) 2026 Zhambyl Yermagambet
"""Split Codex canonical translation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.codex.canonical import translator_dependencies as dependencies
from harness.impl.codex.canonical.translator_core_values import (
    FINISHED_PHASE,
    SHELL_SUBJECT,
    SKILL_SUBJECT,
    STARTED_PHASE,
)

if TYPE_CHECKING:
    from harness.impl.codex.canonical.translator_state_models import RecordSource


def child_actor_started(
    raw_event: dependencies.translator_service_dependencies.raw_events.RawEvent,
    metadata: dependencies.record_payload_namespaces.record_session_meta.SessionMetaPayload,
) -> dependencies.translator_service_dependencies.raw_events.TranslationResult:
    """Translate child session metadata into an actor-start event.

    Returns:
        The actor event and its translation decision.

    """
    role: dependencies.translator_domain_values.messaging.ActorRole = (
        dependencies.translator_domain_values.messaging.ActorRole.SIDECAR
        if raw_event.source_type == "sidecar_rollout"
        else dependencies.translator_domain_values.messaging.ActorRole.CHILD
    )
    actor_name = _metadata_actor_name(metadata) or "codex"
    actor_started = dependencies.translator_codex_dependencies.support.event(
        raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "actor",
            str(raw_event.actor_id),
            STARTED_PHASE,
            dependencies.translator_domain_events.event_actor.ActorStarted(actor_name, role),
            occurred_at=dependencies.translator_codex_dependencies.support.timestamp(metadata.timestamp),
        ),
    )
    return dependencies.translator_service_dependencies.raw_events.TranslationResult(
        (actor_started,),
        dependencies.translator_domain_values.records.RecordedTranslationDecision.TRANSLATED,
    )


def child_assignment_started(
    record_source: RecordSource,
    native_turn_id: dependencies.translator_id_dependencies.ids_conversation_types.CodexTurnId,
    turn_id: dependencies.translator_type_dependencies.ids.TurnId,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a child assignment start from its turn and session metadata.

    Returns:
        The assignment event with the recorded actor name, when available.

    """
    metadata = dependencies.translator_codex_dependencies.source_catalog.session_metadata(
        record_source.raw_event.source_name,
    )
    actor_name = _metadata_actor_name(metadata)
    assignment_id = dependencies.translator_id_dependencies.ids_conversation.assignment_id_from_codex_turn(
        native_turn_id,
    )
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "actor_assignment",
            str(assignment_id),
            STARTED_PHASE,
            dependencies.translator_domain_events.event_actor.ActorAssignmentStarted(
                assignment_id,
                dependencies.translator_codex_dependencies.support.content(actor_name or "actor assignment"),
                actor_name=actor_name or None,
            ),
            turn_id=turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )


def _metadata_actor_name(
    metadata: dependencies.record_payload_namespaces.record_session_meta.SessionMetaPayload | None,
) -> str:
    metadata_source = (
        metadata.source
        if metadata
        and isinstance(
            metadata.source,
            dependencies.record_payload_namespaces.record_session_sources.SessionMetaSource,
        )
        else None
    )
    spawn = metadata_source.subagent.thread_spawn if metadata_source and metadata_source.subagent else None
    agent_path = spawn.agent_path if spawn else ""
    basename = (agent_path or "").rsplit("/", 1)[-1]
    return basename.replace("_", " ").strip()


def child_assignment_finished(
    record_source: RecordSource,
    record: dependencies.record_canonical_namespaces.record_task_records.TaskCompleteRecord,
    native_turn_id: dependencies.translator_id_dependencies.ids_conversation_types.CodexTurnId,
    turn_id: dependencies.translator_type_dependencies.ids.TurnId,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build a successful assignment finish from a completed child turn.

    Returns:
        The assignment finish with its final message, when present.

    """
    assignment_id = dependencies.translator_id_dependencies.ids_conversation.assignment_id_from_codex_turn(
        native_turn_id,
    )
    result = None
    if record.last:
        result = dependencies.translator_codex_dependencies.support.content(record.last, markdown=True)
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            "actor_assignment",
            str(assignment_id),
            FINISHED_PHASE,
            dependencies.translator_domain_events.event_actor.ActorAssignmentFinished(
                assignment_id,
                dependencies.translator_domain_values.outcomes.Outcome.SUCCEEDED,
                result,
                None,
            ),
            turn_id=turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )


def cancelled_shell_event(
    record_source: RecordSource,
    shell_id: dependencies.translator_type_dependencies.ids.ShellId,
    turn_id: dependencies.translator_type_dependencies.ids.TurnId,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build the finish event for an interrupted shell.

    Returns:
        A cancelled shell finish with the source time and turn identifier.

    """
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            SHELL_SUBJECT,
            str(shell_id),
            FINISHED_PHASE,
            dependencies.translator_domain_events.event_shell.ShellFinished(
                shell_id,
                dependencies.translator_domain_values.outcomes.Outcome.CANCELLED,
                None,
                None,
            ),
            turn_id=turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )


def cancelled_output_event(
    record_source: RecordSource,
    shell_id: dependencies.translator_type_dependencies.ids.ShellId,
    turn_id: dependencies.translator_type_dependencies.ids.TurnId,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build an output finish for an interrupted background shell.

    Returns:
        A cancelled shell-output event.

    """
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            SHELL_SUBJECT,
            str(shell_id),
            "output_finished",
            dependencies.translator_domain_events.event_shell.ShellOutputFinished(
                shell_id,
                dependencies.translator_domain_values.outcomes.Outcome.CANCELLED,
            ),
            turn_id=turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )


def cancelled_skill_event(
    record_source: RecordSource,
    skill_id: dependencies.translator_type_dependencies.ids.SkillId,
    turn_id: dependencies.translator_type_dependencies.ids.TurnId,
) -> dependencies.translator_type_dependencies.event_base.CanonicalEvent[
    dependencies.translator_type_dependencies.event_base.EventPayload
]:
    """Build the finish event for an interrupted skill.

    Returns:
        A cancelled skill finish with the source time and turn identifier.

    """
    return dependencies.translator_codex_dependencies.support.event(
        record_source.raw_event,
        dependencies.translator_service_dependencies.CanonicalEventDraft(
            SKILL_SUBJECT,
            str(skill_id),
            FINISHED_PHASE,
            dependencies.translator_domain_events.event_resource.SkillFinished(
                skill_id,
                dependencies.translator_domain_values.outcomes.Outcome.CANCELLED,
                None,
            ),
            turn_id=turn_id,
            occurred_at=record_source.occurred_at,
        ),
    )
