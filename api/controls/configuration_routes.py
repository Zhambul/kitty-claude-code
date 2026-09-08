# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide rewind, compaction, and model control routes."""

from fastapi import APIRouter, Response

from api.common.models.fields import SessionIdPath
from api.controls.control_responses import CONTROL_RESPONSES, respond
from api.controls.models.apply_rewind_request import ApplyRewindRequest
from api.controls.models.compact_request import CompactRequest
from api.controls.models.control_outcome_response import ControlOutcomeResponse
from api.controls.models.open_rewind_request import OpenRewindRequest
from api.controls.models.select_effort_request import SelectEffortRequest
from api.controls.models.select_model_request import SelectModelRequest
from app.provider_controls import Controls
from domain.ids import SessionId

router = APIRouter()


@router.post("/api/sessions/{session_id}/controls/open-rewind", responses=CONTROL_RESPONSES)
def open_rewind(
    session_id: SessionIdPath,
    open_rewind_request: OpenRewindRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Open rewind.

    Returns:
        The control outcome response.

    """
    return respond(controls.open_rewind(open_rewind_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/apply-rewind", responses=CONTROL_RESPONSES)
def apply_rewind(
    session_id: SessionIdPath,
    apply_rewind_request: ApplyRewindRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Apply rewind.

    Returns:
        The control outcome response.

    """
    return respond(controls.apply_rewind(apply_rewind_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/compact", responses=CONTROL_RESPONSES)
def compact(
    session_id: SessionIdPath,
    compact_request: CompactRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Compact a session.

    Returns:
        The control outcome response.

    """
    return respond(controls.compact(compact_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/select-model", responses=CONTROL_RESPONSES)
def select_model(
    session_id: SessionIdPath,
    select_model_request: SelectModelRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Select a model.

    Returns:
        The control outcome response.

    """
    return respond(controls.select_model(select_model_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/select-effort", responses=CONTROL_RESPONSES)
def select_effort(
    session_id: SessionIdPath,
    select_effort_request: SelectEffortRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Select model effort.

    Returns:
        The control outcome response.

    """
    return respond(controls.select_effort(select_effort_request.request(SessionId(session_id))), response)
