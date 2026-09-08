# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata api snapshot."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

from core.git_status import RepositoryStatus
from core.repository import RepositoryQueries
from harness.models import session as session_models
from repository.contract import session_data as session_data_contract
from repository.contract.sessions import SessionRepository
from terminal.adapter import TerminalAdapter
from tests import canonical_sessiondata_api_values as api_values

if TYPE_CHECKING:
    from domain import (
        session_state,
    )


class _SessionDataDependencies:
    """Store the mocked services used by session-data tests."""

    def __init__(self) -> None:
        """Create independent storage, terminal, and repository mocks."""
        self.read_model = Mock(spec=session_data_contract.SessionDataRepository)
        self.terminal = Mock(spec=TerminalAdapter)
        self.repositories = Mock(spec=RepositoryQueries)
        self.session_storage = Mock(spec=SessionRepository)


def _listed_session_dependencies(
    live_session: session_state.SessionData,
    parked_session: session_state.SessionData,
) -> _SessionDataDependencies:
    dependencies = _SessionDataDependencies()
    dependencies.read_model.high_water_cursor.return_value = api_values.SESSION_LIST_CURSOR
    dependencies.read_model.running.return_value = (live_session, parked_session)
    dependencies.terminal.live_sessions.return_value = frozenset((api_values.SESSION,))
    dependencies.repositories.status.return_value = RepositoryStatus(branch="main", worktree=None, dirty=False)
    dependencies.repositories.project_directory.return_value = api_values.WORKING_DIRECTORY
    dependencies.session_storage.find.return_value = session_models.Session(
        api_values.SESSION,
        api_values.LEAD,
        "/work/session.jsonl",
        api_values.WORKING_DIRECTORY,
        project_directory=api_values.WORKING_DIRECTORY,
    )
    return dependencies


def _finished_session_dependencies(
    finished_session: session_state.SessionData,
) -> _SessionDataDependencies:
    dependencies = _SessionDataDependencies()
    dependencies.read_model.high_water_cursor.return_value = api_values.FINISHED_SESSION_CURSOR
    dependencies.read_model.running.return_value = ()
    dependencies.read_model.read.return_value = finished_session
    dependencies.terminal.live_sessions.return_value = frozenset((api_values.SESSION,))
    dependencies.terminal.window_for_session.return_value = "shell-window"
    dependencies.repositories.status.return_value = None
    dependencies.repositories.project_directory.return_value = api_values.WORKING_DIRECTORY
    dependencies.session_storage.find.return_value = None
    return dependencies
