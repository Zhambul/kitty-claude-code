# Copyright (c) 2026 Zhambyl Yermagambet
"""Immutable values for composer drafts and queued messages."""

from dataclasses import dataclass

from domain.ids import RequestId


@dataclass(frozen=True)
class ComposerDraft:
    """Hold text that a person has not sent to a session."""

    text: str
    origin: str
    sequence: float


@dataclass(frozen=True)
class QueuedMessage:
    """Hold one message that waits for harness delivery."""

    request_id: RequestId
    text: str


@dataclass(frozen=True)
class ComposerQueue:
    """Hold the messages that wait for harness delivery."""

    messages: tuple[QueuedMessage, ...]
    origin: str


@dataclass(frozen=True)
class ComposerState:
    """Hold the current draft and queued messages for a session."""

    draft: ComposerDraft | None
    queue: ComposerQueue | None
