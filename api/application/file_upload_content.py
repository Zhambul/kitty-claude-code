# Copyright (c) 2026 Zhambyl Yermagambet
"""Decode and validate staged upload content."""

import base64
import binascii
from http import HTTPStatus

from api.application.file_input import RejectedInputAudit, reject_input
from app.provider_audit_storage import Recorder
from core.daemon.contract import UPLOAD_MAX

UPLOAD_AUDIT_ACTION = "web-upload"


def decoded_upload(encoded_content: str, safe_name: str, audit: Recorder) -> bytes:
    """Return valid decoded upload content.

    Returns:
        The decoded bytes.

    Raises:
        reject_input: If the content is not valid.

    """
    try:
        file_bytes = base64.b64decode(encoded_content, validate=True)
    except (binascii.Error, ValueError):
        raise reject_input(
            audit,
            UPLOAD_AUDIT_ACTION,
            "invalid base64",
            RejectedInputAudit(why="bad base64", name=safe_name),
        ) from None
    if not file_bytes:
        raise reject_input(
            audit,
            UPLOAD_AUDIT_ACTION,
            "empty file",
            RejectedInputAudit(why="empty file", name=safe_name),
        )
    if len(file_bytes) > UPLOAD_MAX:
        raise reject_input(
            audit,
            UPLOAD_AUDIT_ACTION,
            "file too large",
            RejectedInputAudit(why="too large", bytes=len(file_bytes)),
            code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
        )
    return file_bytes
