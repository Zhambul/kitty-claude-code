# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the clipboard file matching route."""

import pathlib

from fastapi import APIRouter

from api.application.file_input import claimed_session_id
from api.application.models.files.clipboard_files_request import ClipboardFilesRequest
from api.application.models.files.clipboard_matches_response import ClipboardMatchesResponse
from api.dependencies import Policy
from app.provider_audit_storage import Recorder
from audit.documents import AuditDocument
from core import clipboard

router = APIRouter()


class ClipboardAudit(AuditDocument):
    """Represent clipboard audit."""

    session_id: str
    names: tuple[str, ...]
    matched: int
    paths: tuple[str, ...]


@router.post("/api/application/clipboard-files")
def clipboard_files(
    clipboard_files_request: ClipboardFilesRequest,
    policy: Policy,
    audit: Recorder,
) -> ClipboardMatchesResponse:
    """Resolve the host paths for matching pasted files.

    Returns:
        The matching host paths.

    """
    session_id = claimed_session_id(policy, clipboard_files_request.session_id)
    limited_names = clipboard_files_request.names[: clipboard.FILES_MAX]
    names = [pathlib.Path(name).name for name in limited_names]
    matched = clipboard.match(names)
    audit.state_file(
        "",
        "",
        "web-clipboard",
        ClipboardAudit(
            session_id=session_id,
            names=tuple(names),
            matched=len(matched),
            paths=tuple(matched),
        ),
    )
    return ClipboardMatchesResponse(paths=tuple(matched))
