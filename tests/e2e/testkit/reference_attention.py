# Copyright (c) 2026 Zhambyl Yermagambet
"""Define E2E references for attention and browser actions."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import SessionRef


@dataclass(frozen=True)
class QuestionRef:
    """Represent one question attention item."""

    session: SessionRef
    attention_id: str
    question_id: str
    turn_name: str


@dataclass(frozen=True)
class PlanRef:
    """Represent one plan attention item."""

    session: SessionRef
    attention_id: str
    turn_name: str


@dataclass(frozen=True)
class BrowserActionRef:
    """Represent one browser action."""

    session: SessionRef
    cursor_before: int


@dataclass(frozen=True)
class BrowserSessionFormRef:
    """Represent one browser session form."""

    source: SessionRef | None
    request_start_index: int
    resume_request_start_index: int | None = None
