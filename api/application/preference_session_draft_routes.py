# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide session composer and dialog draft routes."""

from fastapi import APIRouter

from api.application.models.preferences.composer_draft_request import ComposerDraftRequest
from api.application.models.preferences.dialog_draft_request import DialogDraftRequest
from api.common.models.fields import SessionIdPath
from api.common.models.replies.saved_response import SavedResponse
from app.provider_session_application import SessionApplication
from domain.dialogs import AnswerSelection
from domain.ids import AttentionId, SessionId

router = APIRouter()


@router.post("/api/sessions/{session_id}/application/composer-draft")
def save_composer_draft(
    session_id: SessionIdPath,
    composer_draft_request: ComposerDraftRequest,
    workspace: SessionApplication,
) -> SavedResponse:
    """Save the composer draft.

    Returns:
        The saved response.

    """
    saved = workspace.save_composer_draft(
        SessionId(session_id),
        composer_draft_request.text,
        composer_draft_request.origin,
        composer_draft_request.sequence,
    )
    return SavedResponse(saved=saved)


@router.post("/api/sessions/{session_id}/application/dialog-draft")
def save_dialog_draft(
    session_id: SessionIdPath,
    dialog_draft_request: DialogDraftRequest,
    workspace: SessionApplication,
) -> SavedResponse:
    """Save the dialog draft.

    Returns:
        The saved response.

    """
    selections = tuple(AnswerSelection(answer.selected, answer.other) for answer in dialog_draft_request.answers)
    workspace.save_dialog_draft(
        SessionId(session_id),
        AttentionId(dialog_draft_request.attention_id),
        selections,
        dialog_draft_request.origin,
    )
    return SavedResponse()
