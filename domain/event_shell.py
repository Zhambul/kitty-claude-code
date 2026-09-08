# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical payloads for shell command activity."""

from dataclasses import dataclass

from domain.content import Content
from domain.event_base import EventPayload
from domain.ids import ShellId
from domain.outcomes import ExecutionMode, Outcome, OutputMode, ProgressStream
from domain.work_state import ShellFollowUntil


@dataclass(frozen=True)
class ShellStarted(EventPayload):
    """Record the start of a shell command."""

    shell_id: ShellId
    command: Content
    execution: ExecutionMode
    description: str | None


@dataclass(frozen=True)
class ShellProgressed(EventPayload):
    """Record one ordered shell output update."""

    shell_id: ShellId
    ordinal: int
    stream: ProgressStream
    content: Content
    mode: OutputMode


@dataclass(frozen=True)
class ShellInputProvided(EventPayload):
    """Record input or an input close for a running shell."""

    shell_id: ShellId
    content: Content | None
    closed: bool


@dataclass(frozen=True)
class ShellFinished(EventPayload):
    """Record the final launch outcome of a shell command."""

    shell_id: ShellId
    outcome: Outcome
    result: Content | None
    exit_code: int | None


@dataclass(frozen=True)
class ShellOutputLocated(EventPayload):
    """Record the output file that belongs to a shell command."""

    shell_id: ShellId
    source_path: str
    chunk_source_type: str
    delete_source: bool
    initial_size: int
    initial_modified_at: int
    wait_for_source_change: bool
    until: ShellFollowUntil


@dataclass(frozen=True)
class ShellBackgrounded(EventPayload):
    """Record that a foreground shell command moved to the background."""

    shell_id: ShellId


@dataclass(frozen=True)
class ShellOutputFinished(EventPayload):
    """Record the true end of a background shell output stream."""

    shell_id: ShellId
    outcome: Outcome | None = None
