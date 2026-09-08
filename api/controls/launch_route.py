# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the session launch route."""

from http import HTTPStatus

from fastapi import APIRouter, Response

from api.controls import mapper
from api.controls.control_responses import LAUNCH_RESPONSES, LAUNCH_STATUS
from api.controls.models.launch_response import LaunchResponse
from api.controls.models.launch_session_request import LaunchSessionRequest
from app.provider_harness_registry import Registry
from domain.ids import HarnessName
from harness.models.launch import LaunchResult, LaunchStatus

router = APIRouter()


@router.post("/api/sessions", status_code=HTTPStatus.ACCEPTED, responses=LAUNCH_RESPONSES)
def launch(
    launch_session_request: LaunchSessionRequest,
    harnesses: Registry,
    response: Response,
) -> LaunchResponse:
    """Launch a session.

    Returns:
        The launch response.

    """
    plugin = harnesses.plugin(HarnessName(launch_session_request.harness))
    request = launch_session_request.request()
    if plugin.launcher is None:
        result = LaunchResult(LaunchStatus.REJECTED, reason="unsupported launch")
    else:
        result = plugin.launcher.launch(request)
    response.status_code = LAUNCH_STATUS[result.status]
    return mapper.launch(result, request.working_directory)
