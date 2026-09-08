# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide global new-session preference routes."""

from fastapi import APIRouter

from api.application.models.preferences.new_session_draft_request import NewSessionDraftRequest
from api.application.models.preferences.new_session_preferences_request import NewSessionPreferencesRequest
from api.common.models.replies.saved_response import SavedResponse
from app.provider_application_preferences import ApplicationPreferences
from domain.ids import HarnessName

router = APIRouter()


@router.post("/api/application/new-session-preferences")
def save_new_session_preferences(
    new_session_preferences_request: NewSessionPreferencesRequest,
    application_preferences: ApplicationPreferences,
) -> SavedResponse:
    """Save the new-session form preferences.

    Returns:
        The saved response.

    """
    harness_text = new_session_preferences_request.harness
    application_preferences.save_new_session_preferences(
        working_directory=new_session_preferences_request.working_directory or None,
        harness=HarnessName(harness_text) if harness_text else None,
        model=new_session_preferences_request.model or None,
        effort=new_session_preferences_request.effort or None,
    )
    return SavedResponse()


@router.post("/api/application/new-session-drafts")
def save_new_session_draft(
    new_session_draft_request: NewSessionDraftRequest,
    application_preferences: ApplicationPreferences,
) -> SavedResponse:
    """Save the new-session draft.

    Returns:
        The saved response.

    """
    saved = application_preferences.save_new_session_draft(
        new_session_draft_request.working_directory,
        new_session_draft_request.text,
        new_session_draft_request.sequence,
    )
    return SavedResponse(saved=saved)
