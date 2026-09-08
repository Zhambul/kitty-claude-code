# Copyright (c) 2026 Zhambyl Yermagambet
"""Define session stream state and service contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from audit.failures import ErrorRecorder as ErrorRecorder
from core.change_signal import ChangeSignal
from dashboard.services.workspace import SessionApplicationSnapshot

if TYPE_CHECKING:
    from domain.ids import SessionId
    from repository.contract.session_data import SessionDelta


@dataclass
class SessionFrameState:
    """Store one session stream position and application snapshot."""

    cursor: int
    application: SessionApplicationSnapshot | None
    heartbeat_at: float
    application_read_at: float


@dataclass(frozen=True)
class SessionStreamServices:
    """Contain the services for one session stream route."""

    read_model: SessionDeltaReader
    audit: ErrorRecorder
    session_application: SessionSnapshotReader | None = None
    changes: ChangeSignal = field(default_factory=ChangeSignal)


class SessionDeltaReader(Protocol):
    """Read changes for one session."""

    def delta(self, session_id: SessionId, cursor: int) -> SessionDelta:
        """Return changes after a cursor."""
        ...


class SessionSnapshotReader(Protocol):
    """Read the application state for one session."""

    def snapshot(self, session_id: SessionId) -> SessionApplicationSnapshot:
        """Return the session application state."""
        ...
