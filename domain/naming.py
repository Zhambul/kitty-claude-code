# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable automatic-title jobs."""

from dataclasses import dataclass
from enum import StrEnum

from domain.ids import SessionId


class NamingJobState(StrEnum):
    """Show the current state of an automatic naming job."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class NamingJob:
    """Describe one durable automatic naming job."""

    key: str
    session_id: SessionId
    prompt: str
    state: NamingJobState = NamingJobState.PENDING
    title: str | None = None
    error: str | None = None
