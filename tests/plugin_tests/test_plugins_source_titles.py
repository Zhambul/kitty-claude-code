# Copyright (c) 2026 Zhambyl Yermagambet
"""Native title source tests."""

import sqlite3
from pathlib import Path

import pytest

from domain import (
    event_session,
    ids as domain_ids,
    work_state,
)
from harness.impl.claude_code.canonical.sources import (
    ClaudeTranscriptRawEventSource,
)
from harness.impl.codex.canonical import title as codex_title
from harness.impl.codex.canonical.source_readers import (
    CodexRolloutRawEventSource,
)
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.source_title_support import codex_title_fixture

TITLE_CHANGE_COUNT = 3
SOURCE_BATCH_SIZE = 100


def test_codex_title_source_reports_native_title(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify codex title source reports native title changes."""
    title_fixture = codex_title_fixture(monkeypatch, tmp_path)

    initial = title_fixture.read(None)
    assert initial.payload == event_session.SessionTitleChanged(
        fixture.GENERATED_TITLE_TEXT, work_state.TitleOrigin.AUTOMATIC,
    )

    title_fixture.titles[0] = codex_title.CodexNativeTitle("Chosen title", work_state.TitleOrigin.AUTOMATIC)
    title_fixture.marker[0] = 2
    changed = title_fixture.read(initial.raw_event.source_position)
    assert changed.payload == event_session.SessionTitleChanged("Chosen title", work_state.TitleOrigin.AUTOMATIC)

    title_fixture.titles[0] = codex_title.CodexNativeTitle(
        fixture.GENERATED_TITLE_TEXT,
        work_state.TitleOrigin.AUTOMATIC,
    )
    title_fixture.marker[0] = TITLE_CHANGE_COUNT
    cleared = title_fixture.read(changed.raw_event.source_position)
    assert cleared.payload == event_session.SessionTitleChanged(
        fixture.GENERATED_TITLE_TEXT, work_state.TitleOrigin.AUTOMATIC,
    )
    assert (
        len(
            {
                initial.raw_event.raw_event_id,
                changed.raw_event.raw_event_id,
                cleared.raw_event.raw_event_id,
            },
        )
        == TITLE_CHANGE_COUNT
    )
    assert title_fixture.source.read(cleared.raw_event.source_position) == ()


def test_codex_title_repo_uses_home_that_owns(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verify codex title repository uses the home that owns the rollout."""
    session_id = "00000000-0000-0000-0000-000000000001"
    source_path = (
        tmp_path
        / fixture.SESSIONS
        / fixture.YEAR_TEXT
        / fixture.MONTH_TEXT
        / "24"
        / f"rollout-2026-08-24T00-00-00-{session_id}.jsonl"
    )
    source_path.parent.mkdir(parents=True)
    source_path.write_text("")
    database_path = tmp_path / "state_9.sqlite"
    with sqlite3.connect(database_path) as connection:
        connection.execute("CREATE TABLE threads(id TEXT PRIMARY KEY, title TEXT)")
        connection.execute(
            "INSERT INTO threads(id, title) VALUES(?, ?)",
            (session_id, "Initial title"),
        )
    monkeypatch.setenv(fixture.CODEX_HOME_ENV, str(tmp_path / "another-codex-home"))
    repository = codex_title.CodexThreadTitleRepository(str(tmp_path / "another-codex-home"))

    assert repository.read_title(source_path.as_posix()) == codex_title.CodexNativeTitle(
        "Initial title",
        work_state.TitleOrigin.AUTOMATIC,
    )
    assert repository.set_title(source_path.as_posix(), "Parked title") == "renamed"
    assert repository.read_title(source_path.as_posix()) == codex_title.CodexNativeTitle(
        "Parked title",
        work_state.TitleOrigin.AUTOMATIC,
    )


def test_codex_title_repo_prefers_and_writes(tmp_path: Path) -> None:
    """Verify codex title repository prefers and writes the native name."""
    session_id = "00000000-0000-0000-0000-000000000002"
    source_path = (
        tmp_path
        / fixture.SESSIONS
        / fixture.YEAR_TEXT
        / fixture.MONTH_TEXT
        / "25"
        / (f"rollout-2026-08-25T00-00-00-{session_id}.jsonl")
    )
    source_path.parent.mkdir(parents=True)
    source_path.write_text("")
    database_path = tmp_path / "state_10.sqlite"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE threads(id TEXT PRIMARY KEY, title TEXT, name TEXT)",
        )
        connection.execute(
            "INSERT INTO threads(id, title, name) VALUES(?, ?, ?)",
            (session_id, fixture.GENERATED_TITLE_TEXT, "Native name"),
        )
    repository = codex_title.CodexThreadTitleRepository(tmp_path.as_posix())

    assert repository.read_title(source_path.as_posix()) == codex_title.CodexNativeTitle(
        "Native name",
        work_state.TitleOrigin.AUTOMATIC,
    )
    assert (
        repository.set_title(source_path.as_posix(), "Dashboard name") == "renamed",
        repository.read_title(source_path.as_posix()),
    ) == (
        True,
        codex_title.CodexNativeTitle(
            "Dashboard name",
            work_state.TitleOrigin.AUTOMATIC,
        ),
    )
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT title, name FROM threads WHERE id=?",
            (session_id,),
        ).fetchone() == (fixture.GENERATED_TITLE_TEXT, "Dashboard name")
        connection.execute(
            "UPDATE threads SET name=NULL WHERE id=?",
            (session_id,),
        )
        connection.commit()
    assert repository.read_title(source_path.as_posix()) == codex_title.CodexNativeTitle(
        fixture.GENERATED_TITLE_TEXT,
        work_state.TitleOrigin.AUTOMATIC,
    )

    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "UPDATE threads SET name='   ' WHERE id=?",
            (session_id,),
        )
        connection.commit()
    assert repository.read_title(source_path.as_posix()) == codex_title.CodexNativeTitle(
        fixture.GENERATED_TITLE_TEXT,
        work_state.TitleOrigin.AUTOMATIC,
    )


@pytest.mark.parametrize("source_type", [ClaudeTranscriptRawEventSource, CodexRolloutRawEventSource])
def test_file_sources_read_bounded_batches(
    tmp_path: Path,
    source_type: type[ClaudeTranscriptRawEventSource | CodexRolloutRawEventSource],
) -> None:
    """Verify file sources read bounded batches and resume by position."""
    source_path = tmp_path / "source.jsonl"
    line = b'{"type":"example"}\n'
    source_path.write_bytes(line * fixture.SOURCE_LINE_COUNT)
    source = source_type(
        Session(
            domain_ids.SessionId(fixture.SESSION_ONE_ID),
            domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
            source_path.as_posix(),
            fixture.WORK_PATH,
        ).source_context,
    )

    first_batch = source.read(None)
    assert len(first_batch) == SOURCE_BATCH_SIZE

    second_batch = source.read(first_batch[-1].source_position)
    assert len(second_batch) == 1
    assert source.read(second_batch[-1].source_position) == ()
