# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep the durable composer queue aligned with canonical prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from domain.composer import QueuedMessage
from domain.content import content_text
from domain.event_conversation import MessageCreated, MessageQueued
from domain.messaging import MessagePhase, MessageRole
from harness.contract import CanonicalEventReaction

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from domain.ids import RequestId, SessionId
    from domain.workspace import SessionWorkspace


class QueuedPromptWorkspace(Protocol):
    """Store queue operations that canonical prompts need."""

    def find(self, session_id: SessionId) -> SessionWorkspace | None:
        """Return one session workspace."""
        ...

    def remove_queued_message(self, session_id: SessionId, request_id: RequestId) -> None:
        """Remove one queued message."""
        ...

    def enqueue_composer_message(
        self,
        session_id: SessionId,
        queued_message: QueuedMessage,
        origin: str,
    ) -> None:
        """Add one queued message."""
        ...


def _prompt_matches(queued_text: str, delivered_text: str) -> bool:
    normalized_text = queued_text.strip()
    return bool(normalized_text) and delivered_text.strip().endswith(normalized_text)


class QueuedPromptCanonicalEventReaction(CanonicalEventReaction):
    """Keep a read-model mirror of messages in the harness queue."""

    def __init__(self, queued_prompt_workspace: QueuedPromptWorkspace) -> None:
        """Initialize the object."""
        self.workspaces = queued_prompt_workspace

    def react(self, canonical_event: CanonicalEvent[EventPayload]) -> None:
        """Apply one queue or prompt event."""
        payload = canonical_event.payload
        if isinstance(payload, MessageQueued):
            self.workspaces.enqueue_composer_message(
                canonical_event.session_id,
                QueuedMessage(payload.request_id, content_text(payload.content)),
                "harness",
            )
            return
        workspace = self.workspaces.find(canonical_event.session_id)
        queue = None if workspace is None else workspace.queue
        if queue is None or not queue.messages:
            return
        if (
            not isinstance(payload, MessageCreated)
            or payload.role != MessageRole.USER
            or payload.phase != MessagePhase.PROMPT
        ):
            return
        delivered_text = content_text(payload.content)
        delivered_item = next(
            (message for message in queue.messages if _prompt_matches(message.text, delivered_text)),
            None,
        )
        if delivered_item is not None:
            self.workspaces.remove_queued_message(
                canonical_event.session_id,
                delivered_item.request_id,
            )
