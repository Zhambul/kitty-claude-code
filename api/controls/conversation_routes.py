# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide question and plan control routes."""

from fastapi import APIRouter, Response

from api.common.models.fields import SessionIdPath
from api.controls.control_responses import CONTROL_RESPONSES, respond
from api.controls.models.answer_question_request import AnswerQuestionRequest
from api.controls.models.control_outcome_response import ControlOutcomeResponse
from api.controls.models.decide_plan_request import DecidePlanRequest
from api.controls.models.read_plan_choices_request import ReadPlanChoicesRequest
from app.provider_controls import Controls
from domain.ids import SessionId

router = APIRouter()


@router.post("/api/sessions/{session_id}/controls/answer-question", responses=CONTROL_RESPONSES)
def answer_question(
    session_id: SessionIdPath,
    answer_question_request: AnswerQuestionRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Answer a question.

    Returns:
        The control outcome response.

    """
    return respond(controls.answer_question(answer_question_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/read-plan-choices", responses=CONTROL_RESPONSES)
def read_plan_choices(
    session_id: SessionIdPath,
    read_plan_choices_request: ReadPlanChoicesRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Read plan choices.

    Returns:
        The control outcome response.

    """
    return respond(controls.read_plan_choices(read_plan_choices_request.request(SessionId(session_id))), response)


@router.post("/api/sessions/{session_id}/controls/decide-plan", responses=CONTROL_RESPONSES)
def decide_plan(
    session_id: SessionIdPath,
    decide_plan_request: DecidePlanRequest,
    controls: Controls,
    response: Response,
) -> ControlOutcomeResponse:
    """Decide a plan.

    Returns:
        The control outcome response.

    """
    return respond(controls.decide_plan(decide_plan_request.request(SessionId(session_id))), response)
