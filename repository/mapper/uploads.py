# Copyright (c) 2026 Zhambyl Yermagambet
"""Row DTO to a stored attachment."""

from __future__ import annotations

from domain.ids import SessionId
from domain.uploads import StoredUpload
from repository.model.uploads import UploadRow


def stored_upload(upload_row: UploadRow) -> StoredUpload:
    """Return the stored upload.

    Returns:
        Stored upload.

    """
    return StoredUpload(
        upload_id=upload_row.upload_id,
        session_id=SessionId(upload_row.session_id) if upload_row.session_id else None,
        name=upload_row.name,
        media_type=upload_row.media_type,
        byte_size=upload_row.byte_size,
        stored_path=upload_row.stored_path,
        created_at=upload_row.created_at,
    )


def upload_row(stored_upload: StoredUpload) -> UploadRow:
    """Return the upload row.

    Returns:
        Upload row.

    """
    return UploadRow(
        upload_id=stored_upload.upload_id,
        session_id=stored_upload.session_id or SessionId(""),
        name=stored_upload.name,
        media_type=stored_upload.media_type,
        byte_size=stored_upload.byte_size,
        stored_path=stored_upload.stored_path,
        created_at=stored_upload.created_at,
    )
