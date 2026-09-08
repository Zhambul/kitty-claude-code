# Copyright (c) 2026 Zhambyl Yermagambet
"""The SQLite audit repositories against a real database."""

from __future__ import annotations

from typing import TYPE_CHECKING

from audit import records as audit_records
from domain import ids as domain_ids
from repository.impl.sqlite import audit as sqlite_audit, audit_read as sqlite_audit_read, databases as sqlite_databases

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

SESSION = domain_ids.SessionId("session-one")
AUDIT_ERROR_TIME = 5.0
STREAM_OUTPUT_LINE_COUNT = 12
AUDIT_DATABASE_NAME = "audit.db"


def test_errors_are_written_and_counted_per(tmp_path: Path) -> None:
    """Verify errors are written and counted per session."""
    database = sqlite_databases.audit_database(str(tmp_path / AUDIT_DATABASE_NAME))
    writes = sqlite_audit.SqliteAuditWriteRepository(database)
    reads = sqlite_audit_read.SqliteAuditReadRepository(sqlite_databases.read_only(database))
    writes.record_error(
        audit_records.ApplicationErrorRecord(
            SESSION,
            "script",
            "where",
            "trace",
            "context",
            1,
            AUDIT_ERROR_TIME,
        ),
    )
    stored = reads.errors_for_session(SESSION)
    assert [error.action for error in stored] == ["where"]
    assert reads.error_counts() == {SESSION: 1}


def test_audit_writer_never_raises_when_its_file(tmp_path: Path) -> None:
    """Verify the audit writer never raises when its file is unusable."""
    unusable = sqlite_databases.audit_database(str(tmp_path / "missing" / "nested" / AUDIT_DATABASE_NAME))
    unusable.path = str(tmp_path)
    writes = sqlite_audit.SqliteAuditWriteRepository(unusable)
    writes.record_error(
        audit_records.ApplicationErrorRecord(domain_ids.SessionId(""), "script", "f", "t", "c", 1, 1.0),
    )
    writes.record_state_file(
        audit_records.StateFileRecord(domain_ids.SessionId(""), "p", "a", "c", "state document", 1, 1.0),
    )
    writes.record_spawn(
        audit_records.SpawnRecord(domain_ids.SessionId(""), "spawn source", 2, "[]", "why", 1.0),
    )
    assert (
        writes.open_stream(
            audit_records.StreamOpened(
                domain_ids.SessionId(""),
                "kind",
                domain_ids.ActorId(""),
                domain_ids.TaskId(""),
                "",
                1,
                1.0,
            ),
        )
        is None
    )
    writes.close_stream(None, "done", 0)


def test_stream_row_is_opened_and_closed_through(tmp_path: Path) -> None:
    """Verify a stream row is opened and closed through its handle."""
    database = sqlite_databases.audit_database(str(tmp_path / AUDIT_DATABASE_NAME))
    writes = sqlite_audit.SqliteAuditWriteRepository(database)
    stream_handle = writes.open_stream(
        audit_records.StreamOpened(
            SESSION,
            "mirror",
            domain_ids.ActorId(""),
            domain_ids.TaskId(""),
            "",
            1,
            1.0,
        ),
    )
    assert stream_handle is not None
    writes.close_stream(stream_handle, "finished", STREAM_OUTPUT_LINE_COUNT)
    with database.read() as connection:
        row = connection.execute("SELECT * FROM streams WHERE id=?", (stream_handle.stream_id,)).fetchone()
    assert (row["end_reason"], row["lines_emitted"]) == (
        "finished",
        STREAM_OUTPUT_LINE_COUNT,
    )


def test_the_audit_is_a_no_op_when_switched_off(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify the audit is a no op when switched off."""
    monkeypatch.setenv("BAQYLAU_AUDIT", "0")
    database = sqlite_databases.audit_database(str(tmp_path / AUDIT_DATABASE_NAME))
    writes = sqlite_audit.SqliteAuditWriteRepository(database)
    writes.record_error(audit_records.ApplicationErrorRecord(SESSION, "script", "f", "t", "c", 1, 1.0))
    reads = sqlite_audit_read.SqliteAuditReadRepository(sqlite_databases.read_only(database))
    assert reads.errors_for_session(SESSION) == ()
