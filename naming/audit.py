# Copyright (c) 2026 Zhambyl Yermagambet
"""Declared audit documents for automatic naming."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit.documents import AuditDocument

if TYPE_CHECKING:
    from audit.recorder import AuditRecorder

AUTOMATIC_TITLE_ACTION = "automatic_title"


class NamingAudit(AuditDocument):
    """Describe one automatic naming operation for audit storage."""

    job_key: str
    status: str | None = None
    title: str | None = None
    error_type: str | None = None
    error: str | None = None


def record_job_state(
    recorder: AuditRecorder,
    job_key: str,
    session_id: str,
    status: str,
    title: str | None = None,
) -> None:
    """Write the state of one naming job to the audit log."""
    recorder.state_file(
        session_id,
        "",
        AUTOMATIC_TITLE_ACTION,
        NamingAudit(job_key=job_key, title=title, status=status),
    )
