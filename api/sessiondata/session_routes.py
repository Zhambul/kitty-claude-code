# Copyright (c) 2026 Zhambyl Yermagambet
"""Serve one session-data aggregate."""

from fastapi import APIRouter

from api.common.models.fields import SessionIdPath
from api.sessiondata import lookups, mapper
from api.sessiondata.models.session_data import SessionDataResponse
from app.provider_harness_sessions import Sessions
from app.provider_runtime import Repositories
from app.provider_session_storage import SessionDataStore
from app.provider_terminal import Terminal
from domain.ids import SessionId

router = APIRouter()


@router.get("/sessionData/{session_id}")
def session_data(
    session_id: SessionIdPath,
    read_model: SessionDataStore,
    terminal: Terminal,
    repositories: Repositories,
    session_storage: Sessions,
) -> SessionDataResponse:
    """Return one session-data aggregate.

    Returns:
        The session-data response.

    """
    session_record = lookups.found(read_model, SessionId(session_id))
    return mapper.session_data(
        session_record,
        live=lookups.is_live(terminal, session_record),
        repository_status=repositories.status(
            session_record.session.working_directory,
        ),
        project_directory=lookups.project_directory(
            session_storage,
            repositories,
            session_record.session.session_id,
            session_record.session.working_directory,
        ),
    )
