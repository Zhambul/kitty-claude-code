# Copyright (c) 2026 Zhambyl Yermagambet
"""Check complete and partial source batches."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from domain.ids import ActorId, SessionId
from engine.interpret.dependencies import InterpreterDependencies
from engine.interpret.puller import (
    _read_and_record,  # noqa: PLC2701 -- Check batch drain and partial-line resume as one unit.
)
from harness.impl.codex.canonical.source_readers import CodexRolloutRawEventSource
from harness.models.raw_events import RawEventSourceContext

if TYPE_CHECKING:
    from pathlib import Path

COMPLETE_SOURCE_LINES = 251


@pytest.fixture
def transcript(tmp_path: Path) -> Path:
    """Write complete records followed by one partial record.

    Returns:
        The source file path.

    """
    path = tmp_path / "session.jsonl"
    path.write_bytes(b"".join((b"{}\n" * COMPLETE_SOURCE_LINES, b"{")))
    return path


@pytest.fixture
def source(transcript: Path) -> CodexRolloutRawEventSource:
    """Open the test transcript as a Codex source.

    Returns:
        The source reader.

    """
    return CodexRolloutRawEventSource(
        RawEventSourceContext(
            session_id=SessionId("session"),
            lead_actor_id=ActorId("lead"),
            actor_id=ActorId("lead"),
            parent_actor_id=None,
            source_reference=str(transcript),
        ),
    )


@pytest.fixture
def dependencies() -> Mock:
    """Build a record-storage probe.

    Returns:
        The interpreter dependencies with a mock repository.

    """
    return Mock(spec=InterpreterDependencies, repositories=Mock())


def test_source_notice_drains_all_batches(
    transcript: Path,
    source: CodexRolloutRawEventSource,
    dependencies: Mock,
) -> None:
    """Read all complete lines, then retain the incomplete line for its next write."""
    record = dependencies.repositories.raw_events.record
    _read_and_record(dependencies, source, None)
    assert [
        len(call.args[0]) for call in record.call_args_list
    ] == [100, 100, 51]
    batch = record.call_args.args[0]
    position = batch[-1].source_position
    with transcript.open("ab") as stream:
        stream.write(b"}\n")
    record.reset_mock()
    _read_and_record(dependencies, source, position)
    record.assert_called_once()
    batch = record.call_args.args[0]
    assert len(batch) == 1
    assert batch[0].payload == b"{}\n"
