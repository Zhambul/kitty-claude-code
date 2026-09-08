# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for turns, messages, and reasoning."""

from dataclasses import dataclass

from domain.content import Content
from domain.event_base import EventPayload
from domain.ids import ActorId, MessageId, ReasoningId, RequestId
from domain.messaging import MessagePhase, MessageRole
from domain.outcomes import Outcome


@dataclass(frozen=True)
class TurnStarted(EventPayload):
    """Record the start of one agent turn."""

    prompt_message_id: MessageId | None


@dataclass(frozen=True)
class TurnFinished(EventPayload):
    """Record the successful or failed end of an agent turn."""

    final_message_id: MessageId | None
    outcome: Outcome


@dataclass(frozen=True)
class TurnAborted(EventPayload):
    """Record an agent turn that stopped before completion."""

    reason: str | None


@dataclass(frozen=True)
class MessageCreated(EventPayload):
    """Record one message between session participants."""

    message_id: MessageId
    role: MessageRole
    content: Content
    phase: MessagePhase | None
    reply_to: MessageId | None
    recipient_actor_id: ActorId | None = None


@dataclass(frozen=True)
class MessageQueued(EventPayload):
    """Record a message that a harness accepted into its queue."""

    request_id: RequestId
    content: Content


@dataclass(frozen=True)
class ReasoningCreated(EventPayload):
    """Record one visible agent reasoning block."""

    reasoning_id: ReasoningId
    content: Content
