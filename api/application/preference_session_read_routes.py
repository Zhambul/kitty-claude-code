# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide session application state read routes."""

from fastapi import APIRouter

from api.application.mapper import preferences as mapper
from api.application.models.preferences.session_application_response import SessionApplicationResponse
from api.common.models.fields import SessionIdPath
from app.provider_session_application import SessionApplication
from domain.ids import SessionId

router = APIRouter()


@router.get("/api/sessions/{session_id}/application")
def session_application(
    session_id: SessionIdPath,
    workspace: SessionApplication,
) -> SessionApplicationResponse:
    """Return the browser-owned session state.

    Returns:
        The session application state.

    """
    return mapper.session_application(workspace.snapshot(SessionId(session_id)))
