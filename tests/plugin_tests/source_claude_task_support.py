# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for Claude task source tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from domain import event_work, ids, work_state
from harness.impl.claude_code.canonical.sources import (
    ClaudeTaskRawEventSource,
)
from harness.impl.claude_code.canonical.translator import ClaudeCanonicalTranslator
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_events import payloads

if TYPE_CHECKING:
    import pytest


@dataclass
class ClaudeTaskSourceFixture:
    """Hold a task file, its editable document, and the source that reads it."""

    task_path: Path
    task: dict[str, str | list[str]]
    source: ClaudeTaskRawEventSource


def claude_task_source_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> ClaudeTaskSourceFixture:
    """Write a pending Claude task and create its source reader.

    Returns:
        The task file, document, and source for the isolated configuration directory.

    """
    monkeypatch.setenv(fixture.CLAUDE_CONFIG_DIR_ENV, tmp_path.as_posix())
    task_directory = tmp_path / "tasks" / "session-6165ab88"
    task_directory.mkdir(parents=True)
    task_path = task_directory / "1.json"
    task: dict[str, str | list[str]] = {
        fixture.ID_FIELD: fixture.ONE_TEXT,
        "subject": fixture.RUN_TESTS_TEXT,
        fixture.DESCRIPTION_FIELD: "Run the focused suite",
        "activeForm": "Running tests",
        "owner": fixture.WORKER_ONE_ID,
        fixture.STATUS_FIELD: "pending",
        "blocks": [],
        "blockedBy": [],
    }
    task_path.write_text(json.dumps(task), encoding=fixture.TEXT_ENCODING)
    session = Session(
        ids.SessionId("6165ab88-21b7-4b54-a2dd-c25a8ecb0b59"),
        ids.ActorId("6165ab88-21b7-4b54-a2dd-c25a8ecb0b59:lead"),
        fixture.WORK_SESSION_JSONL_PATH,
        fixture.WORK_PATH,
    )
    return ClaudeTaskSourceFixture(
        task_path,
        task,
        ClaudeTaskRawEventSource(session, tmp_path.as_posix()),
    )


def assert_created_task(
    source_fixture: ClaudeTaskSourceFixture,
) -> tuple[str, ids.CanonicalEventId]:
    """Check the task creation event and the unchanged-source read.

    Returns:
        The final source position and the task creation event identity.

    """
    raw_events = source_fixture.source.read(None)
    assert [event.source_type for event in raw_events] == ["tasks", "task_list"]
    position = raw_events[-1].source_position
    assert source_fixture.source.read(position) == ()
    created_event = ClaudeCanonicalTranslator().translate(raw_events[0]).canonical_events[0]
    assert created_event.payload == event_work.TaskChanged(
        ids.TaskId(fixture.ONE_TEXT),
        fixture.RUN_TESTS_TEXT,
        "Run the focused suite",
        work_state.TaskState.PENDING,
        ids.ActorId(fixture.WORKER_ONE_ID),
    )
    return position, created_event.event_id


def assert_updated_task(
    source_fixture: ClaudeTaskSourceFixture,
    position: str,
    created_event_id: ids.CanonicalEventId,
) -> str:
    """Change a task to in-progress and check its update event.

    Returns:
        The final source position after the task update.

    """
    source_fixture.task[fixture.STATUS_FIELD] = "in_progress"
    source_fixture.task_path.write_text(
        json.dumps(source_fixture.task),
        encoding=fixture.TEXT_ENCODING,
    )
    raw_events = source_fixture.source.read(position)
    updated_event = payloads(
        ClaudeCanonicalTranslator().translate(raw_events[0]),
        event_work.TaskChanged,
    )[0]
    assert updated_event.payload.state == "in_progress"
    assert updated_event.event_id != created_event_id
    return raw_events[-1].source_position


def assert_deleted_task(source_fixture: ClaudeTaskSourceFixture, position: str) -> None:
    """Delete the test task and check that the task list becomes empty."""
    source_fixture.task_path.unlink()
    raw_events = source_fixture.source.read(position)
    assert [event.source_type for event in raw_events] == ["task_list"]
    membership = ClaudeCanonicalTranslator().translate(raw_events[0]).canonical_events[0].payload
    assert membership == event_work.TaskListChanged(ids.TaskListId("session"), ())
