# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide direct session control gesture routes."""

from fastapi import APIRouter, Response

from api.common.models.fields import SessionIdPath
from api.controls.control_responses import CONTROL_RESPONSES, respond
from api.controls.models.auto_name_session_request import AutoNameSessionRequest
from api.controls.models.background_request import BackgroundRequest
from api.controls.models.close_session_request import CloseSessionRequest
from api.controls.models.control_outcome_response import ControlOutcomeResponse
from api.controls.models.interrupt_request import InterruptRequest
from api.controls.models.rename_session_request import RenameSessionRequest
from api.controls.models.send_text_request import SendTextRequest
from app.provider_controls import Controls
from domain.ids import SessionId

router = APIRouter()


@router.post("/api/sessions/{session_id}/controls/send-text", responses=CONTROL_RESPONSES)
def send_text(
    session_id: SessionIdPath,
    send_text_request: SendTextRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Send text to a session.

    Returns:
        The control outcome response.

    """
    return respond(controls.send_text(send_text_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/interrupt", responses=CONTROL_RESPONSES)
def interrupt(
    session_id: SessionIdPath,
    interrupt_request: InterruptRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Interrupt a session.

    Returns:
        The control outcome response.

    """
    return respond(controls.interrupt(interrupt_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/background", responses=CONTROL_RESPONSES)
def background(
    session_id: SessionIdPath,
    background_request: BackgroundRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Move the blocked command to the background.

    Returns:
        The control outcome response.

    """
    return respond(controls.background(background_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/close-session", responses=CONTROL_RESPONSES)
def close_session(
    session_id: SessionIdPath,
    close_session_request: CloseSessionRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Close a session.

    Returns:
        The control outcome response.

    """
    return respond(controls.close_session(close_session_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/rename-session", responses=CONTROL_RESPONSES)
def rename_session(
    session_id: SessionIdPath,
    rename_session_request: RenameSessionRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Rename a session.

    Returns:
        The control outcome response.

    """
    return respond(controls.rename_session(rename_session_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/auto-name-session", responses=CONTROL_RESPONSES)
def auto_name_session(
    session_id: SessionIdPath,
    auto_name_session_request: AutoNameSessionRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Name a session automatically.

    Returns:
        The control outcome response.

    """
    return respond(controls.auto_name_session(auto_name_session_request.request(SessionId(session_id))), response)
