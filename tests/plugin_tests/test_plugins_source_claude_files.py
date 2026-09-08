# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude child and task source tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.claude_code.canonical.sources import (
    ClaudeTaskRawEventSource,
    ClaudeTranscriptRawEventSource,
)
from tests.plugin_tests.source_claude_child_support import (
    assert_claude_child_source_context,
    assert_claude_child_source_refresh,
    claude_child_sources_fixture,
)
from tests.plugin_tests.source_claude_task_support import (
    assert_created_task,
    assert_deleted_task,
    assert_updated_task,
    claude_task_source_fixture,
)

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

EXPECTED_SOURCE_COUNT = 4


def test_claude_source_factory_includes_child(tmp_path: Path) -> None:
    """Verify claude source factory includes child transcripts."""
    source_fixture = claude_child_sources_fixture(tmp_path)

    sources = source_fixture.factory.for_session(source_fixture.session)

    assert len(sources) == EXPECTED_SOURCE_COUNT
    assert isinstance(sources[2], ClaudeTaskRawEventSource)
    child_source = sources[3]
    assert isinstance(child_source, ClaudeTranscriptRawEventSource)
    assert_claude_child_source_context(child_source)
    assert source_fixture.factory.for_session(source_fixture.session) is sources

    assert_claude_child_source_refresh(source_fixture, sources)


def test_claude_task_source_captures_full_updates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify claude task source captures full updates and deletion."""
    source_fixture = claude_task_source_fixture(tmp_path, monkeypatch)
    position, created_event_id = assert_created_task(source_fixture)
    position = assert_updated_task(source_fixture, position, created_event_id)
    assert_deleted_task(source_fixture, position)
