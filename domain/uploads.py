# Copyright (c) 2026 Zhambyl Yermagambet
"""An attachment the browser staged for a session's composer.

The BYTES stay on disk: an attachment is delivered to the harness as an `@path`
mention, so a real file has to exist. What is stored here is the record of it —
without which the uploads directory grows without bound and a stray file is
unattributable to any session.
"""

from dataclasses import dataclass

from domain.ids import SessionId, UploadId


@dataclass(frozen=True)
class StoredUpload:
    """Describe an uploaded file that waits for delivery to a session."""

    upload_id: UploadId
    session_id: SessionId | None
    name: str
    media_type: str
    byte_size: int
    stored_path: str
    created_at: float
