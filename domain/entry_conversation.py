# Copyright (c) 2026 Zhambyl Yermagambet
"""Feed entry bodies for turns, messages, and reasoning."""

from dataclasses import dataclass

from domain.content import Content
from domain.entry_base import EntryBody, TurnState
from domain.ids import ActorId, MessageId, ReasoningId
from domain.messaging import MessagePhase, MessageRole


@dataclass(frozen=True)
class TurnStartedBody(EntryBody):
    """Mark the start of one agent turn."""

    prompt_message_id: MessageId | None = None


@dataclass(frozen=True)
class TurnFinishedBody(EntryBody):
    """Record how one agent turn ended."""

    state: TurnState


@dataclass(frozen=True)
class MessageBody(EntryBody):
    """Record one message that a session participant sent."""

    message_id: MessageId
    role: MessageRole
    phase: MessagePhase | None
    content: Content
    recipient_actor_id: ActorId | None = None
    reply_to: MessageId | None = None


@dataclass(frozen=True)
class ReasoningBody(EntryBody):
    """Record one visible agent reasoning block."""

    reasoning_id: ReasoningId
    content: Content
