# Copyright (c) 2026 Zhambyl Yermagambet
"""Validate common application file input."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from fastapi import HTTPException

from audit.documents import AuditDocument

if TYPE_CHECKING:
    from api.config import Settings
    from audit.recorder import AuditRecorder


class RejectedInputAudit(AuditDocument):
    """Represent rejected input audit."""

    ok: Literal[False] = False
    why: str
    name: str | None = None
    bytes: int | None = None


def reject_input(
    audit_recorder: AuditRecorder,
    action: str,
    message: str,
    rejected_input_audit: RejectedInputAudit,
    code: int = 400,
) -> HTTPException:
    """Audit and reject malformed application input.

    Returns:
        The HTTP exception.

    """
    audit_recorder.state_file("", "", action, rejected_input_audit)
    return HTTPException(code, message)


def claimed_session_id(settings: Settings, session_id: str | None) -> str:
    """Return the valid supplied session ID, or an empty string.

    Returns:
        The valid session ID, or an empty string.

    """
    if not isinstance(session_id, str):
        return ""
    if not settings.session_id_pattern.match(session_id):
        return ""
    return session_id
