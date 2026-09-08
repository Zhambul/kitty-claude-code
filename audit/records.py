# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed records that the operational audit repository stores."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import RootModel

from domain.ids import ActorId, SessionId, TaskId


class SpawnArguments(RootModel[tuple[str, ...]]):
    """Hold the argument vector of a spawned process."""


@dataclass(frozen=True)
class ApplicationErrorRecord:
    """Hold a swallowed application exception for storage."""

    session_id: SessionId
    script: str
    function: str
    traceback: str
    context: str
    process_id: int
    timestamp: float


@dataclass(frozen=True)
class ApplicationError:
    """Hold a stored application exception for dashboard display."""

    error_id: int
    timestamp: float
    component: str
    action: str
    traceback: str
    context: str


@dataclass(frozen=True)
class StateFileRecord:
    """Hold an audited state-file operation."""

    session_id: SessionId
    path: str
    action: str
    content: str
    script: str
    process_id: int
    timestamp: float


@dataclass(frozen=True)
class SpawnRecord:
    """Hold an audited child-process spawn."""

    session_id: SessionId
    parent_script: str
    child_process_id: int
    argv: str
    purpose: str
    timestamp: float


@dataclass(frozen=True)
class StreamOpened:
    """Hold the start of an audited output stream."""

    session_id: SessionId
    kind: str
    agent_id: ActorId
    task_id: TaskId
    source_path: str
    process_id: int
    started_at: float


@dataclass(frozen=True)
class StreamHandle:
    """Identify one open audited output stream."""

    stream_id: int
