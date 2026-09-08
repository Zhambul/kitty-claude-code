# Copyright (c) 2026 Zhambyl Yermagambet
"""Map conversation entry bodies to API responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.mapper import values
from api.sessiondata.models import entry as entry_models
from domain import entry_conversation as conversation_bodies

if TYPE_CHECKING:
    from domain import entry_base


def map_body(entry_body: entry_base.EntryBody) -> entry_models.EntryBodyResponse | None:
    """Return the API response for a conversation entry body.

    Returns:
        The API response for a conversation entry body.

    """
    if isinstance(entry_body, conversation_bodies.TurnStartedBody):
        return entry_models.TurnStartedBodyResponse(
            prompt_message_id=(None if entry_body.prompt_message_id is None else str(entry_body.prompt_message_id)),
        )
    if isinstance(entry_body, conversation_bodies.TurnFinishedBody):
        return entry_models.TurnFinishedBodyResponse(state=entry_body.state)
    if isinstance(entry_body, conversation_bodies.MessageBody):
        return entry_models.MessageBodyResponse(
            message_id=str(entry_body.message_id),
            role=entry_body.role,
            phase=entry_body.phase,
            content=values.content(entry_body.content),
            recipient_actor_id=(None if entry_body.recipient_actor_id is None else str(entry_body.recipient_actor_id)),
            reply_to=None if entry_body.reply_to is None else str(entry_body.reply_to),
        )
    if isinstance(entry_body, conversation_bodies.ReasoningBody):
        return entry_models.ReasoningBodyResponse(
            reasoning_id=entry_body.reasoning_id,
            content=values.content(entry_body.content),
        )
    return None
