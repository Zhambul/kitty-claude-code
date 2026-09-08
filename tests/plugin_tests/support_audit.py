# Copyright (c) 2026 Zhambyl Yermagambet
"""Audit support for plugin tests."""

from audit.recorder import AuditRecorder
from repository.impl.sqlite.audit import SqliteAuditWriteRepository
from repository.impl.sqlite.databases import audit_database


def silent_audit() -> AuditRecorder:
    """Create an audit recorder for the test audit database.

    Returns:
        An audit recorder for the test audit database.

    """
    return AuditRecorder(SqliteAuditWriteRepository(audit_database()))
