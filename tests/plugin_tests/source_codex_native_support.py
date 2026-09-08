# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for native Codex source tests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from domain import (
    ids as domain_ids,
)
from harness.impl.codex.canonical.source_readers import (
    CodexRolloutRawEventSource,
)
from harness.impl.codex.canonical.sources import CodexRawEventSources
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture

if TYPE_CHECKING:
    from pathlib import Path


def write_native_codex_rollout(child_path: Path) -> None:
    """Write a child rollout with inherited and child-owned records."""
    records = [
        {
            fixture.TYPE_FIELD: fixture.SESSION_META_ID,
            fixture.TIMESTAMP_FIELD: fixture.AUGUST_TIMESTAMP_TEXT,
            fixture.PAYLOAD_FIELD: {
                fixture.CWD_FIELD: fixture.WORK_PATH,
                fixture.THREAD_SOURCE: fixture.SUBAGENT,
                fixture.PARENT_THREAD_ID_FIELD: fixture.PARENT_SESSION_ID,
                fixture.TIMESTAMP_FIELD: fixture.AUGUST_TIMESTAMP_TEXT,
            },
        },
        {
            fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
            fixture.PAYLOAD_FIELD: {
                fixture.TYPE_FIELD: "user_message",
                fixture.MESSAGE_FIELD: "parent replay",
            },
        },
        {
            fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
            fixture.PAYLOAD_FIELD: {
                fixture.TYPE_FIELD: fixture.TASK_STARTED_ID,
                fixture.STARTED_AT: 1786701599,
            },
        },
        {
            fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
            fixture.PAYLOAD_FIELD: {
                fixture.TYPE_FIELD: fixture.TASK_STARTED_ID,
                fixture.STARTED_AT: 1786701600,
            },
        },
        {
            fixture.TYPE_FIELD: fixture.EVENT_MSG_ID,
            fixture.PAYLOAD_FIELD: {
                fixture.TYPE_FIELD: "agent_message",
                fixture.MESSAGE_FIELD: "child work",
            },
        },
    ]
    lines = [json.dumps(record) for record in records]
    lines.append("")
    child_path.write_text("\n".join(lines), encoding="utf-8")


def same_objects[SourceObject](first: tuple[SourceObject, ...], second: tuple[SourceObject, ...]) -> bool:
    """Return true when two tuples contain the same object instances.

    Returns:
        True when two tuples contain the same object instances.

    """
    return all(
        left is right
        for left, right in zip(first, second, strict=True)
    )


def rollout_directory(tmp_path: Path, day: str) -> Path:
    """Return one fixture directory below the native Codex rollout root.

    Returns:
        One fixture directory below the native Codex rollout root.

    """
    month_directory = tmp_path / fixture.SESSIONS / fixture.YEAR_TEXT / fixture.MONTH_TEXT
    return month_directory / day


def rollout_path(tmp_path: Path, day: str, file_name: str) -> Path:
    """Return one fixture path below the native Codex rollout directory.

    Returns:
        One fixture path below the native Codex rollout directory.

    """
    return rollout_directory(tmp_path, day) / file_name


def native_session_directory(tmp_path: Path) -> Path:
    """Return the fixture directory for native Codex sessions.

    Returns:
        The fixture directory for native Codex sessions.

    """
    return rollout_directory(tmp_path, fixture.FOURTEEN_TEXT)


def native_codex_child_source(
    tmp_path: Path,
) -> CodexRolloutRawEventSource:
    """Build the source for a native child rollout.

    Returns:
        The child rollout source found for the parent session.

    """
    child_path = rollout_path(
        tmp_path,
        fixture.FOURTEEN_TEXT,
        "rollout-2026-08-14T10-00-00-child-one.jsonl",
    )
    child_path.parent.mkdir(parents=True)
    write_native_codex_rollout(child_path)
    session = Session(
        session_id=domain_ids.SessionId(fixture.PARENT_SESSION_ID),
        lead_actor_id=domain_ids.ActorId(fixture.PARENT_SESSION_LEAD_ID),
        source_reference=str(tmp_path / fixture.NOT_A_CODEX_SESSION_JSONL_PATH),
        working_directory=fixture.WORK_PATH,
    )
    sources = CodexRawEventSources(tmp_path.as_posix()).for_session(session)
    assert len(sources) == 1
    child_source = sources[0]
    assert isinstance(child_source, CodexRolloutRawEventSource)
    return child_source
