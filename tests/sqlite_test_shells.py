# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide sqlite test shells."""

from __future__ import annotations

from tests import (
    sqlite_domain_dependencies as domain_dependencies,
    sqlite_library_dependencies as library_dependencies,
    sqlite_repository_dependencies as repository_dependencies,
    sqlite_test_fixtures,
    sqlite_test_models,
    sqlite_value_dependencies as standard_dependencies,
)


def dismissed_session_ids(
    dismissals: repository_dependencies.sqlite_preferences.SqliteTaskDismissalRepository,
) -> list[domain_dependencies.domain_ids.SessionId]:
    """Find test sessions that have dismissed tasks.

    Returns:
        The matching identifiers among the four test sessions.

    """
    return [
        domain_dependencies.domain_ids.SessionId(f"s{candidate_index}")
        for candidate_index in range(4)
        if dismissals.dismissed_task_ids(domain_dependencies.domain_ids.SessionId(f"s{candidate_index}"))
    ]


def an_upload() -> domain_dependencies.upload_models.StoredUpload:
    """Create a text upload record for tests.

    Returns:
        The fixed upload record without creating a file.

    """
    upload_id = domain_dependencies.domain_ids.UploadId("u")
    return domain_dependencies.upload_models.StoredUpload(upload_id, None, "n", "text/plain", 1, "/test-data/n", 0)


def track_connection(
    opened_connections: list[standard_dependencies.sqlite3.Connection],
    native_connect: sqlite_test_models.NativeConnect,
) -> standard_dependencies.sqlite3.Connection:
    """Open a connection and add it to the test record.

    Returns:
        The new connection.

    """
    connection = native_connect()
    opened_connections.append(connection)
    return connection


@standard_dependencies.pytest.fixture
def migration(tmp_path: standard_dependencies.Path) -> sqlite_test_models.MigrationDatabase:
    """Create a database that a migration test can move to the current schema.

    Returns:
        A database that a migration test can move to the current schema.

    """
    return sqlite_test_models.MigrationDatabase(tmp_path)


def restore_version_ten_schema(connection: standard_dependencies.sqlite3.Connection) -> None:
    """Restore the version ten raw event schema for a migration test."""
    sqlite_test_fixtures.restore_version_eleven_schema(connection)
    connection.execute("ALTER TABLE raw_events DROP COLUMN payload_codec")


def shell_started_event(
    event_id: str,
    shell_id: domain_dependencies.domain_ids.ShellId,
    command: library_dependencies.domain_content.TextContent,
) -> library_dependencies.event_base.CanonicalEvent[library_dependencies.event_base.EventPayload]:
    """Create a foreground shell start event.

    Returns:
        The event with the supplied shell and command.

    """
    return standard_dependencies.replace(
        sqlite_test_fixtures.a_started_event(event_id),
        payload=library_dependencies.event_shell.ShellStarted(
            shell_id, command, domain_dependencies.outcomes.ExecutionMode.FOREGROUND, None,
        ),
    )


def shell_finished_event(
    event_id: str,
    shell_id: domain_dependencies.domain_ids.ShellId,
    outcome: domain_dependencies.outcomes.Outcome,
    content: library_dependencies.domain_content.TextContent | None,
) -> library_dependencies.event_base.CanonicalEvent[library_dependencies.event_base.EventPayload]:
    """Create a shell finish event from the test result.

    Returns:
        The event with the supplied outcome and test exit code.

    """
    return standard_dependencies.replace(
        sqlite_test_fixtures.a_started_event(event_id),
        payload=library_dependencies.event_shell.ShellFinished(
            shell_id, outcome, content, sqlite_test_fixtures.shell_exit_code(content),
        ),
    )
