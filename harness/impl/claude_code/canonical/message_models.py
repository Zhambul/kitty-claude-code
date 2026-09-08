# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Claude Code message translation models."""

from __future__ import annotations

from dataclasses import dataclass

from domain import ids as domain_ids
from domain.event_base import CanonicalEvent, EventPayload
from domain.messaging import MessageRole
from domain.references import ModelReference
from harness.impl.claude_code.canonical import records, toolcalls
from harness.impl.claude_code.canonical.turns import TurnSemantics
from harness.models import raw_events
from harness.models.selections import SelectionSemantics


@dataclass(frozen=True)
class TranscriptSource:
    """Keep the raw event and parsed transcript source identity."""

    raw_event: raw_events.RawEvent
    document: records.TranscriptDocument
    native_identity: str
    occurred_at: float | None


@dataclass(frozen=True)
class TranscriptSemantics:
    """Keep tool, turn, selection, and actor state for message translation."""

    tool_calls: toolcalls.ToolCallSemantics
    turns: TurnSemantics
    selections: SelectionSemantics
    actor_started: bool
    recovered_turn_id: domain_ids.TurnId | None


@dataclass(frozen=True)
class PromptInterruption:
    """Track the interrupted turn and whether its abort was emitted."""

    turn_id: domain_ids.TurnId | None
    abort_already_emitted: bool


@dataclass(frozen=True)
class PromptMessage:
    """Keep a prompt's role, interruption state, and created event."""

    role: MessageRole
    interruption: PromptInterruption
    created: CanonicalEvent[EventPayload]


@dataclass(frozen=True)
class AssistantModel:
    """Keep the native model identifier and resolved model reference."""

    model_name: str | None
    reference: ModelReference | None


@dataclass(frozen=True)
class AssistantResponse:
    """Keep assistant message blocks, turn completion, and model details."""

    message: records.MessageObject | None
    blocks: list[records.MessageContentBlock]
    ends_turn: bool
    last_text_index: int
    model: AssistantModel
