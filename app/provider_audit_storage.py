# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide operational audit repositories and recorder."""

from typing import Annotated

from fastapi import Depends

from app import provider_databases as database_providers
from app.injection import singleton
from audit.recorder import AuditRecorder
from repository.contract import audit
from repository.impl.sqlite import audit as sqlite_audit, audit_read as sqlite_audit_read


@singleton
def audit_writes(
    database: database_providers.AuditDb,
) -> audit.AuditWriteRepository:
    """Return operational audit write storage.

    Returns:
        Operational audit write storage.

    """
    return sqlite_audit.SqliteAuditWriteRepository(database)


AuditWrites = Annotated[audit.AuditWriteRepository, Depends(audit_writes)]


@singleton
def recorder(writes: AuditWrites) -> AuditRecorder:
    """Return the injected operational audit recorder.

    Returns:
        Injected operational audit recorder.

    """
    return AuditRecorder(writes)


Recorder = Annotated[AuditRecorder, Depends(recorder)]


@singleton
def audit_reads(
    database: database_providers.AuditReaderDb,
) -> audit.AuditReadRepository:
    """Return operational audit read storage.

    Returns:
        Operational audit read storage.

    """
    return sqlite_audit_read.SqliteAuditReadRepository(database)


AuditReads = Annotated[audit.AuditReadRepository, Depends(audit_reads)]
