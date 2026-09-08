# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the staged upload route."""

from fastapi import APIRouter

from api.application.file_input import claimed_session_id
from api.application.file_upload_content import decoded_upload
from api.application.file_upload_names import safe_attachment_name
from api.application.file_upload_storage import stored_upload, upload_path, write_upload
from api.application.models.files.upload_request import UploadRequest
from api.application.models.files.upload_response import UploadResponse
from api.dependencies import Policy
from api.responses import errors
from app.provider_audit_storage import Recorder
from app.provider_uploads import Uploads

router = APIRouter()
UPLOAD_RESPONSES = errors(
    {
        413: "Decoded bytes over UPLOAD_MAX — the base64 document passed, the file did not.",
        500: "The bytes could not be written; no row was recorded.",
    },
)


@router.post("/api/application/uploads", responses=UPLOAD_RESPONSES)
def upload(upload_request: UploadRequest, uploads: Uploads, policy: Policy, audit: Recorder) -> UploadResponse:
    """Stage one composer attachment and return its path.

    Returns:
        The upload response document.

    """
    session_id = claimed_session_id(policy, upload_request.session_id)
    safe_name = safe_attachment_name(upload_request.name)
    file_bytes = decoded_upload(upload_request.encoded_content, safe_name, audit)
    path = upload_path(session_id, safe_name)
    write_upload(path, file_bytes, session_id, safe_name, audit)
    uploads.record(stored_upload(path, session_id, safe_name, upload_request.mime, len(file_bytes)))
    return UploadResponse(
        path=path,
        name=safe_name,
        mime=upload_request.mime,
        is_image=upload_request.mime in policy.image_mimes,
    )
