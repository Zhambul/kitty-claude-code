# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for usage, context, and compaction reports."""

from dataclasses import dataclass
from decimal import Decimal

from domain.content import Content
from domain.event_base import EventPayload
from domain.references import AccountReference, ModelReference
from domain.usage import TokenUsage, UsageScope


@dataclass(frozen=True)
class UsageReported(EventPayload):
    """Record token usage and cost for one reporting scope."""

    scope: UsageScope
    subject_id: str
    model: ModelReference | None
    account: AccountReference | None
    tokens: TokenUsage
    cumulative: bool
    cost_in_usd: Decimal | None


@dataclass(frozen=True)
class ContextReported(EventPayload):
    """Record context-window usage for one actor."""

    used_tokens: int
    window_tokens: int
    model: ModelReference | None


@dataclass(frozen=True)
class CompactionStarted(EventPayload):
    """Record the context size before compaction starts."""

    before_tokens: int | None


@dataclass(frozen=True)
class CompactionFinished(EventPayload):
    """Record context sizes and retained context after compaction."""

    before_tokens: int | None
    after_tokens: int | None
    context: Content | None = None
