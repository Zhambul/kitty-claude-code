# Copyright (c) 2026 Zhambyl Yermagambet
"""Row shapes for the four session-workspace tables."""

from __future__ import annotations

from dataclasses import dataclass

from domain.ids import AttentionId, RequestId, SessionId


@dataclass(frozen=True)
class SessionWorkspaceRow:
    """Represent session workspace row."""

    session_id: SessionId
    composer_text: str
    composer_origin: str
    composer_sequence: float
    queue_origin: str
    dialog_attention_id: AttentionId | None
    dialog_origin: str


@dataclass(frozen=True)
class ComposerQueueItemRow:
    """Represent composer queue item row."""

    session_id: SessionId
    position: int
    request_id: RequestId
    text: str


@dataclass(frozen=True)
class DialogAnswerRow:
    """Represent dialog answer row."""

    session_id: SessionId
    prompt_index: int
    other_text: str


@dataclass(frozen=True)
class DialogAnswerSelectionRow:
    """Represent dialog answer selection row."""

    session_id: SessionId
    prompt_index: int
    selection_index: int
    selected_value: str
