# Copyright (c) 2026 Zhambyl Yermagambet
"""Define shell entry bodies."""

from __future__ import annotations

from pydantic import BaseModel

from api.common.models.values.content import ContentResponse
from domain.entry_base import RunState
from domain.outcomes import ExecutionMode, OutputMode, ProgressStream


class ShellStartedBodyResponse(BaseModel):
    """Represent a shell-started entry body."""

    shell_id: str
    command: ContentResponse
    execution: ExecutionMode


class ShellOutputBodyResponse(BaseModel):
    """Represent a shell-output entry body."""

    shell_id: str
    stream: ProgressStream
    mode: OutputMode
    content: ContentResponse


class ShellBackgroundedBodyResponse(BaseModel):
    """Represent a shell-backgrounded entry body."""

    shell_id: str


class ShellFinishedBodyResponse(BaseModel):
    """Represent a shell-finished entry body."""

    shell_id: str
    state: RunState
    exit_code: int | None
    result: ContentResponse | None
