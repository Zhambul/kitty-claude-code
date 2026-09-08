# Copyright (c) 2026 Zhambyl Yermagambet
"""Feed entry bodies for shell command activity."""

from dataclasses import dataclass

from domain.content import Content
from domain.entry_base import EntryBody, RunState
from domain.ids import ShellId
from domain.outcomes import ExecutionMode, OutputMode, ProgressStream


@dataclass(frozen=True)
class ShellStartedBody(EntryBody):
    """Record the start of a shell command."""

    shell_id: ShellId
    command: Content
    execution: ExecutionMode


@dataclass(frozen=True)
class ShellOutputBody(EntryBody):
    """Record one shell output chunk exactly as it arrived."""

    shell_id: ShellId
    stream: ProgressStream
    mode: OutputMode
    content: Content


@dataclass(frozen=True)
class ShellBackgroundedBody(EntryBody):
    """Record that a shell command moved to the background."""

    shell_id: ShellId


@dataclass(frozen=True)
class ShellFinishedBody(EntryBody):
    """Record the final state and optional output of a shell command."""

    shell_id: ShellId
    state: RunState
    exit_code: int | None = None
    result: Content | None = None
