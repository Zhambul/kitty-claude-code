# Copyright (c) 2026 Zhambyl Yermagambet
"""Row shapes for the four audit tables."""

from __future__ import annotations

from dataclasses import dataclass

from domain.ids import ActorId, SessionId, TaskId


@dataclass(frozen=True)
class ErrorRow:
    """Represent error row."""

    id: int
    ts: float
    session_id: SessionId
    script: str
    func: str
    traceback: str
    context: str
    pid: int


@dataclass(frozen=True)
class StateFileRow:
    """Represent state file row."""

    id: int
    ts: float
    session_id: SessionId
    path: str
    action: str
    content: str
    script: str
    pid: int


@dataclass(frozen=True)
class SpawnRow:
    """Represent spawn row."""

    id: int
    ts: float
    session_id: SessionId
    parent_script: str
    child_pid: int
    argv: str
    purpose: str


@dataclass(frozen=True)
class ErrorInsertRow:
    """Represent values for one new error row."""

    timestamp: float
    session_id: SessionId
    script: str
    function: str
    traceback: str
    context: str
    process_id: int


@dataclass(frozen=True)
class StateFileInsertRow:
    """Represent values for one new state-file row."""

    timestamp: float
    session_id: SessionId
    path: str
    action: str
    content: str
    script: str
    process_id: int


@dataclass(frozen=True)
class SpawnInsertRow:
    """Represent values for one new spawn row."""

    timestamp: float
    session_id: SessionId
    parent_script: str
    child_process_id: int
    arguments: str
    purpose: str


@dataclass(frozen=True)
class StreamInsertRow:
    """Represent values for one new stream row."""

    session_id: SessionId
    kind: str
    agent_id: ActorId
    task_id: TaskId
    source_path: str
    process_id: int
    started_at: float
