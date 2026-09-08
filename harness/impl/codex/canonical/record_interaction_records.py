# Copyright (c) 2026 Zhambyl Yermagambet
"""Own interaction records models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from harness.impl.codex.canonical.record_context_records import AskQuestionRecord
from harness.impl.codex.ids_session_types import CodexCallId
from harness.impl.codex.model import CodexEffort, CodexModel


@dataclass(frozen=True, kw_only=True)
class ChatRecord:
    """Represent chat record."""

    kind: Literal["chat"] = "chat"
    role: str
    text: str
    synthetic: bool
    phase: str
    turn: str


@dataclass(frozen=True, kw_only=True)
class ThinkRecord:
    """Represent think record."""

    kind: Literal["think"] = "think"
    text: str


@dataclass(frozen=True, kw_only=True)
class PatchCallRecord:
    """Represent patch call record."""

    kind: Literal["patch_call"] = "patch_call"
    patch: str
    call_id: CodexCallId


@dataclass(frozen=True, kw_only=True)
class AskRecord:
    """Represent ask record."""

    kind: Literal["ask"] = "ask"
    call_id: CodexCallId
    questions: tuple[AskQuestionRecord, ...]


@dataclass(frozen=True, kw_only=True)
class PlanRecord:
    """Represent plan record."""

    kind: Literal["plan"] = "plan"
    text: str
    id: str


@dataclass(frozen=True, kw_only=True)
class SettingsRecord:
    """Represent settings record."""

    kind: Literal["settings"] = "settings"
    model: CodexModel | None
    effort: CodexEffort | None


@dataclass(frozen=True, kw_only=True)
class CompactBoundaryRecord:
    """Represent compact boundary record."""

    kind: Literal["compact_boundary"] = "compact_boundary"
    message: str
    context: str
    replaced: int
    window_id: str | int | None
    previous_window_id: str | int | None
