# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code child session records."""

from harness.impl.claude_code.canonical import (
    message_session_dependencies as dependencies,
    message_subject_values as subject_values,
    records,
)
from harness.models import raw_events


def child_session_events(
    raw_event: raw_events.RawEvent,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    """Start a child actor and apply its available metadata.

    Returns:
        The actor-started event followed by optional name and description events.

    """
    metadata = _agent_metadata(raw_event)
    events = [_actor_started_event(raw_event)]
    events.extend(_metadata_events(raw_event, metadata))
    return events


def _actor_started_event(
    raw_event: raw_events.RawEvent,
) -> dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]:
    actor_role = (
        dependencies.messaging.ActorRole.TEAMMATE
        if raw_event.source_type == "teammate_transcript"
        else dependencies.messaging.ActorRole.CHILD
    )
    draft = dependencies.raw_event_builders.CanonicalEventDraft(
        subject_values.ACTOR_SUBJECT,
        str(raw_event.actor_id),
        subject_values.STARTED_PHASE,
        dependencies.event_actor.ActorStarted(str(raw_event.actor_id), actor_role),
    )
    return dependencies.support.event(raw_event, draft)


def _metadata_events(
    raw_event: raw_events.RawEvent,
    metadata: records.AgentMetaFile,
) -> list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]]:
    native_name = str(metadata.name or "").strip()
    description = str(metadata.description or "").strip()
    display_name = native_name or description
    events: list[dependencies.event_base.CanonicalEvent[dependencies.event_base.EventPayload]] = []
    if display_name:
        draft = dependencies.raw_event_builders.CanonicalEventDraft(
            subject_values.ACTOR_SUBJECT,
            str(raw_event.actor_id),
            "name:metadata",
            dependencies.event_actor.ActorNameChanged(display_name),
        )
        events.append(dependencies.support.event(raw_event, draft))
    if description:
        draft = dependencies.raw_event_builders.CanonicalEventDraft(
            subject_values.ACTOR_SUBJECT,
            str(raw_event.actor_id),
            "description:metadata",
            dependencies.event_actor.ActorDescriptionChanged(description),
        )
        events.append(dependencies.support.event(raw_event, draft))
    return events


def _agent_metadata(raw_event: raw_events.RawEvent) -> records.AgentMetaFile:
    if raw_event.source_type not in {"child_transcript", "teammate_transcript"}:
        return records.AgentMetaFile()
    metadata_path = dependencies.pathlib.Path(raw_event.source_name).with_suffix(".meta.json")
    try:
        return _read_agent_metadata(metadata_path)
    except OSError:
        return records.AgentMetaFile()
    except dependencies.ValidationError as error:
        if any(detail["type"] != "json_invalid" for detail in error.errors()):
            raise
        return records.AgentMetaFile()


def _read_agent_metadata(metadata_path: dependencies.pathlib.Path) -> records.AgentMetaFile:
    metadata_text = metadata_path.read_text(encoding="utf-8")
    return records.AgentMetaFile.model_validate_json(metadata_text)
