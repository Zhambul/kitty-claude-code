# Copyright (c) 2026 Zhambyl Yermagambet
"""Derive canonical identity from a Claude Code hook payload."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

from domain.ids import ActorId, SessionId
from harness.impl.claude_code import model
from harness.impl.claude_code.hooks import errors
from harness.impl.claude_code.ids import (
    ClaudeCodeActorId,
    ClaudeCodeSessionId,
    actor_id_from_claude_code,
    lead_actor_id_from_claude_code,
    session_id_from_claude_code,
)

if TYPE_CHECKING:
    from harness.impl.claude_code.canonical.records import HookPayload


@dataclass(frozen=True)
class HookActors:
    """Hold the actors that own one hook event."""

    session_id: SessionId
    lead_actor_id: ActorId
    actor_id: ActorId
    native_actor_id: ClaudeCodeActorId | None


@dataclass(frozen=True)
class HookObservation:
    """Hold the source identity for one hook delivery."""

    actors: HookActors
    hook_name: str
    source_reference: str
    native_event_id: str
    observation_id: str
    source_type: str


@dataclass(frozen=True)
class _HookEventIdentity:
    native_event_id: str
    observation_id: str


def hook_observation(hook_payload: HookPayload, payload: bytes) -> HookObservation:
    """Build source identity for a hook delivery.

    Returns:
        The hook observation.

    Raises:
        MissingTranscriptPathError: If the payload has no transcript path.

    """
    actors = _hook_actors(hook_payload)
    hook_name = hook_payload.hook_event_name or "hook"
    source_reference = hook_payload.transcript_path or ""
    if not source_reference:
        raise errors.MissingTranscriptPathError
    event_identity = _hook_event_identity(hook_payload, payload)
    source_type = _hook_source_type(hook_payload, source_reference, actors)
    return HookObservation(
        actors,
        hook_name,
        source_reference,
        event_identity.native_event_id,
        event_identity.observation_id,
        source_type,
    )


def _hook_actors(hook_payload: HookPayload) -> HookActors:
    if hook_payload.session_id is None:
        raise errors.MissingSessionIdError
    native_session_id = ClaudeCodeSessionId(hook_payload.session_id)
    native_actor_id = ClaudeCodeActorId(hook_payload.agent_id) if hook_payload.agent_id else None
    if hook_payload.hook_event_name in {"SubagentStart", "SubagentStop"} and not native_actor_id:
        raise errors.MissingAgentIdError(hook_payload.hook_event_name)
    lead_actor_id = lead_actor_id_from_claude_code(native_session_id)
    actor_id = actor_id_from_claude_code(ClaudeCodeActorId(native_actor_id)) if native_actor_id else lead_actor_id
    return HookActors(
        session_id_from_claude_code(native_session_id),
        lead_actor_id,
        actor_id,
        native_actor_id,
    )


def _hook_event_identity(hook_payload: HookPayload, payload: bytes) -> _HookEventIdentity:
    native_event_id_value = hook_payload.hook_event_id or hook_payload.uuid
    payload_digest = hashlib.sha256(payload).hexdigest()
    native_event_id = str(native_event_id_value or payload_digest)
    observation_id = native_event_id if native_event_id_value is None else f"{native_event_id}:{payload_digest}"
    return _HookEventIdentity(native_event_id, observation_id)


def _hook_source_type(
    hook_payload: HookPayload,
    source_reference: str,
    hook_actors: HookActors,
) -> str:
    if (
        hook_payload.hook_event_name == "SubagentStart"
        and hook_actors.native_actor_id
        and model.agent_meta(source_reference, hook_actors.actor_id).task_kind == "in_process_teammate"
    ):
        return "teammate_hook"
    return "hook"
