# Copyright (c) 2026 Zhambyl Yermagambet
"""Define the session composer response."""

from pydantic import BaseModel, Field


class ComposerDraftResponse(BaseModel):
    """Represent a composer draft response."""

    text: str
    origin: str
    sequence: float


class QueuedMessageResponse(BaseModel):
    """Represent a queued message response."""

    request_id: str
    text: str


class ComposerQueueResponse(BaseModel):
    """Represent a composer queue response."""

    messages: tuple[QueuedMessageResponse, ...] = Field(alias="items")
    origin: str


class ComposerStateResponse(BaseModel):
    """Represent a composer state response."""

    draft: ComposerDraftResponse | None
    queue: ComposerQueueResponse | None
