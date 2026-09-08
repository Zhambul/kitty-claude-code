# Copyright (c) 2026 Zhambyl Yermagambet
"""Own execution arguments models."""

from __future__ import annotations

from pydantic import BaseModel

from harness.impl.codex.canonical.record_config import FOREIGN, OPEN_FOREIGN
from harness.impl.codex.canonical.record_result_documents import GoalToolResultBlock
from harness.impl.codex.ids_session_types import CodexShellId


class GoalToolResultDocument(BaseModel):
    """Represent goal tool result document."""

    model_config = OPEN_FOREIGN
    goal: GoalToolResultBlock | None = None


class ExecArguments(BaseModel):
    """Represent exec arguments."""

    model_config = FOREIGN
    cmd: str | list[str] | None = None
    command: str | list[str] | None = None
    workdir: str | None = None
    yield_time_ms: int | None = None
    max_output_tokens: int | None = None
    shell: str | None = None
    tty: bool | None = None
    login: bool | None = None
    sandbox_permissions: str | None = None
    justification: str | None = None
    prefix_rule: list[str] | None = None


class StdinArguments(BaseModel):
    """Represent stdin arguments."""

    model_config = FOREIGN
    session_id: CodexShellId | int | None = None
    chars: str | None = None
    yield_time_ms: int | None = None
    max_output_tokens: int | None = None


class AskOption(BaseModel):
    """Represent ask option."""

    model_config = FOREIGN
    label: str | None = None
    description: str | None = None


class AskQuestion(BaseModel):
    """Represent ask question."""

    model_config = FOREIGN
    id: str | None = None
    header: str | None = None
    question: str | None = None
    options: list[AskOption] | None = None


class AskArguments(BaseModel):
    """Represent ask arguments."""

    model_config = FOREIGN
    questions: list[AskQuestion] | None = None


class AskAnswer(BaseModel):
    """Represent ask answer."""

    model_config = FOREIGN
    answers: tuple[str, ...] = ()
