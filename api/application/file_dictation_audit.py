# Copyright (c) 2026 Zhambyl Yermagambet
"""Define dictation audit documents."""

from audit.documents import AuditDocument

DICTATION_AUDIT_ACTION = "web-dictate"
ERROR_AUDIT_LIMIT = 200
SAMPLE_RATE_AUDIT_LIMIT = 40


class DictationAudit(AuditDocument):
    """Represent dictation audit."""

    ok: bool
    why: str | None = None
    rate: int | str | None = None
    working_directory: str | None = None
    keyterms: int | None = None
