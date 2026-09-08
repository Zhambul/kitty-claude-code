# Copyright (c) 2026 Zhambyl Yermagambet
"""Store staged uploads and record their metadata."""

import pathlib
import time
import uuid
from http import HTTPStatus
from typing import Literal

from fastapi import HTTPException

from app.provider_audit_storage import Recorder
from audit.documents import AuditDocument
from dashboard import paths
from domain.ids import SessionId, UploadId
from domain.uploads import StoredUpload


class UploadFailureAudit(AuditDocument):
    """Represent upload failure audit."""

    session_id: str
    name: str
    error: str | None = None
    bytes: int | None = None
    ok: Literal[False] | None = None


def upload_path(session_id: str, safe_name: str) -> str:
    """Return the unique storage path for one upload.

    Returns:
        The upload storage path.

    """
    destination = pathlib.Path(paths.session_uploads_directory(SessionId(session_id)))
    upload_token = uuid.uuid4().hex[:8]
    return str(destination / f"{upload_token}-{safe_name}")


def write_upload(path: str, file_bytes: bytes, session_id: str, safe_name: str, audit: Recorder) -> None:
    """Write one upload and audit a storage failure.

    Raises:
        HTTPException: If the upload cannot be written.

    """
    try:
        _store_upload(path, file_bytes)
    except OSError as error:
        audit.error(
            "",
            "dashboard upload (write failed)",
            UploadFailureAudit(session_id=session_id, name=safe_name, error=str(error)),
        )
        audit.state_file(
            "",
            "",
            "web-upload",
            UploadFailureAudit(
                session_id=session_id,
                name=safe_name,
                bytes=len(file_bytes),
                ok=False,
            ),
        )
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, "could not store upload") from error


def stored_upload(
    path: str,
    session_id: str,
    safe_name: str,
    media_type: str,
    byte_size: int,
) -> StoredUpload:
    """Return metadata for one staged upload.

    Returns:
        The upload metadata.

    """
    return StoredUpload(
        upload_id=UploadId(pathlib.Path(path).name),
        session_id=SessionId(session_id) if session_id else None,
        name=safe_name,
        media_type=media_type,
        byte_size=byte_size,
        stored_path=path,
        created_at=time.time(),
    )


def _store_upload(path: str, file_bytes: bytes) -> None:
    upload_path = pathlib.Path(path)
    upload_path.parent.mkdir(exist_ok=True, parents=True)
    upload_path.write_bytes(file_bytes)
