# Copyright (c) 2026 Zhambyl Yermagambet
"""Own context records models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from harness.impl.codex.canonical.record_usage_payloads import TokenUsageBlock
from harness.impl.codex.model import CodexEffort, CodexModel


@dataclass(frozen=True, kw_only=True)
class PatchFile:
    """Represent patch file."""

    path: str
    change: str | None
    added: int
    removed: int
    previous_path: str | None = None
    diff: str | None = None
    content: str | None = None


@dataclass(frozen=True, kw_only=True)
class AskQuestionRecord:
    """Represent ask question record."""

    id: str
    header: str
    question: str
    options: tuple[AskOptionRecord, ...]


@dataclass(frozen=True, kw_only=True)
class AskOptionRecord:
    """Represent ask option record."""

    label: str
    description: str


@dataclass(frozen=True, kw_only=True)
class TurnContextRecord:
    """Represent turn context record."""

    kind: Literal["turn_context"] = "turn_context"
    model: CodexModel | None
    effort: CodexEffort | None


@dataclass(frozen=True, kw_only=True)
class UsageRecord:
    """Represent usage record."""

    kind: Literal["usage"] = "usage"
    usage: TokenUsageBlock
    last: TokenUsageBlock | None
    window: int | None


@dataclass(frozen=True, kw_only=True)
class PatchRecord:
    """Represent patch record."""

    kind: Literal["patch"] = "patch"
    success: bool
    files: tuple[PatchFile, ...]


@dataclass(frozen=True, kw_only=True)
class CompactRecord:
    """Represent compact record."""

    kind: Literal["compact"] = "compact"
