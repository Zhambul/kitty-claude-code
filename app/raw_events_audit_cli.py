# Copyright (c) 2026 Zhambyl Yermagambet
"""Inspect raw events and their canonical interpretations."""

from __future__ import annotations

import sys
from enum import StrEnum
from typing import TYPE_CHECKING

from app.raw_event_audit_documents import (
    audit_document,
    session_audit_documents,
)
from domain.ids import RawEventId, SessionId
from repository.impl.sqlite.databases import main_database, read_only
from repository.impl.sqlite.raw_event_audits import SqliteRawEventAuditRepository

if TYPE_CHECKING:
    from pydantic import BaseModel

    from repository.contract.facts import RawEventAuditRepository

ARGUMENT_COUNT = 2
SUCCESS_EXIT_CODE = 0
FAILURE_EXIT_CODE = 1
USAGE_EXIT_CODE = 2
USAGE = "usage: baqylau-raw-events-audit raw <raw_event_id> | session <session_id>"


class RawEventAuditCommand(StrEnum):
    """Name each supported raw-event audit command."""

    RAW = "raw"
    SESSION = "session"


def raw_event_audit_repository() -> RawEventAuditRepository | None:
    """Open the main database for read-only raw-event audit access.

    Returns:
        The raw event audit repository.

    """
    database = read_only(main_database())
    if not database.exists():
        _write_error(f"database does not exist: {database.path}")
        return None
    return SqliteRawEventAuditRepository(database)


def main(arguments: list[str] | None = None) -> int:
    """Run the raw-event audit command.

    Returns:
        Integer result.

    """
    selected_arguments = list(
        sys.argv[1:] if arguments is None else arguments,
    )
    if len(selected_arguments) != ARGUMENT_COUNT:
        _write_error(USAGE)
        return USAGE_EXIT_CODE
    try:
        command = RawEventAuditCommand(selected_arguments[0])
    except ValueError:
        _write_error(USAGE)
        return USAGE_EXIT_CODE
    repository = raw_event_audit_repository()
    if repository is None:
        return FAILURE_EXIT_CODE
    identity = selected_arguments[1]
    if command is RawEventAuditCommand.RAW:
        return _write_raw_event(repository, identity)
    document = session_audit_documents(
        repository.audits_for_session(SessionId(identity)),
    )
    _write_document(document)
    return SUCCESS_EXIT_CODE


def _write_raw_event(
    raw_event_audit_repository: RawEventAuditRepository,
    identity: str,
) -> int:
    raw_event_audit = raw_event_audit_repository.audit(RawEventId(identity))
    if raw_event_audit is None:
        _write_error(f"raw event does not exist: {identity}")
        return FAILURE_EXIT_CODE
    _write_document(audit_document(raw_event_audit))
    return SUCCESS_EXIT_CODE


def _write_document(document: BaseModel) -> None:
    sys.stdout.write(f"{document.model_dump_json(indent=2)}\n")


def _write_error(message: str) -> None:
    sys.stderr.write(f"{message}\n")


if __name__ == "__main__":
    sys.exit(main())
