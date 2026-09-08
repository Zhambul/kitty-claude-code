# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the browser dictation grant route."""

import pathlib
from http import HTTPStatus

from fastapi import APIRouter, HTTPException

from api.application.file_dictation_audit import (
    DICTATION_AUDIT_ACTION,
    ERROR_AUDIT_LIMIT,
    SAMPLE_RATE_AUDIT_LIMIT,
    DictationAudit,
)
from api.application.models.files.dictation_grant_response import DictationGrantResponse
from api.application.models.files.dictation_token_request import DictationTokenRequest
from api.responses import errors
from app.provider_audit_storage import Recorder
from audit.documents import ShortErrorAudit
from dashboard import dictate, dictation_credentials

router = APIRouter()
DICTATION_RESPONSES = errors(
    {
        501: "No Deepgram key is configured on this host — the page toasts this one.",
        502: "Deepgram refused to mint the grant.",
    },
)


@router.post("/api/application/dictation-token", responses=DICTATION_RESPONSES)
def dictation_token(dictation_token_request: DictationTokenRequest, audit: Recorder) -> DictationGrantResponse:
    """Mint one short-lived browser dictation grant.

    Returns:
        The dictation grant.

    """
    _validate_dictation_request(dictation_token_request, audit)
    grant = _dictation_grant(audit)
    terms = dictate.keyterms()
    audit.state_file(
        "",
        "",
        DICTATION_AUDIT_ACTION,
        DictationAudit(
            ok=True,
            rate=dictation_token_request.sample_rate,
            working_directory=dictation_token_request.working_directory,
            keyterms=len(terms),
        ),
    )
    return DictationGrantResponse(
        token=grant.access_token,
        expires_in=grant.expires_in,
        ws_url=dictate.ws_url(dictation_token_request.sample_rate, terms),
    )


def _validate_dictation_request(dictation_token_request: DictationTokenRequest, audit: Recorder) -> None:
    sample_rate = dictation_token_request.sample_rate
    if not (dictate.SAMPLE_RATE_MIN <= sample_rate <= dictate.SAMPLE_RATE_MAX):
        audit.state_file(
            "",
            "",
            DICTATION_AUDIT_ACTION,
            DictationAudit(
                ok=False,
                why="bad-rate",
                rate=repr(sample_rate)[:SAMPLE_RATE_AUDIT_LIMIT],
            ),
        )
        raise HTTPException(HTTPStatus.BAD_REQUEST, "bad sample_rate")
    if not dictation_credentials.available():
        audit.state_file("", "", DICTATION_AUDIT_ACTION, DictationAudit(ok=False, why="no-key"))
        raise HTTPException(HTTPStatus.NOT_IMPLEMENTED, "no deepgram key configured")
    working_directory = dictation_token_request.working_directory
    if working_directory is not None and not pathlib.Path(working_directory).is_dir():
        raise HTTPException(HTTPStatus.BAD_REQUEST, "working_directory must be an existing directory")


def _dictation_grant(audit: Recorder) -> dictation_credentials.GrantResponse:
    try:
        return dictation_credentials.grant()
    except Exception as error:
        audit.error(
            "",
            "dashboard dictate (grant failed)",
            ShortErrorAudit(error=(f"{type(error).__name__}: {error}")[:ERROR_AUDIT_LIMIT]),
        )
        audit.state_file("", "", DICTATION_AUDIT_ACTION, DictationAudit(ok=False, why="grant"))
        raise HTTPException(HTTPStatus.BAD_GATEWAY, "token grant failed") from error
