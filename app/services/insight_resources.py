# Copyright (c) 2026 Zhambyl Yermagambet
"""Group dependencies for application insight collection."""

from dataclasses import dataclass
from typing import Protocol

from core.repository import RepositoryQueries
from domain.ids import SessionId
from harness.models.probe import (
    TerminalSessionState,
)
from repository.contract.audit import AuditReadRepository
from repository.contract.session_data import SessionDataRepository


class TerminalSessionReader(Protocol):
    """Read current terminal state for one session."""

    def state(self, session_id: SessionId) -> TerminalSessionState:
        """Return current terminal state for one session."""
        ...


@dataclass(frozen=True)
class ApplicationInsightResources:
    """Hold all readers used to collect application insights."""

    session_data_repository: SessionDataRepository
    terminal_session_reader: TerminalSessionReader
    audit_read_repository: AuditReadRepository
    repository_queries: RepositoryQueries
    top_project_count: int
