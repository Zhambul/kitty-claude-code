# Copyright (c) 2026 Zhambyl Yermagambet
"""Define turn and message entry bodies."""

from __future__ import annotations

from pydantic import BaseModel

from api.common.models.values.content import ContentResponse
from domain.entry_base import TurnState
from domain.messaging import MessagePhase, MessageRole


class TurnStartedBodyResponse(BaseModel):
    """Represent a turn-started entry body."""

    prompt_message_id: str | None


class TurnFinishedBodyResponse(BaseModel):
    """Represent a turn-finished entry body."""

    state: TurnState


class MessageBodyResponse(BaseModel):
    """Represent a message entry body."""

    message_id: str
    role: MessageRole
    phase: MessagePhase | None
    content: ContentResponse
    recipient_actor_id: str | None
    reply_to: str | None


class ReasoningBodyResponse(BaseModel):
    """Represent a reasoning entry body."""

    reasoning_id: str
    content: ContentResponse
