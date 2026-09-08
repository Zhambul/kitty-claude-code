# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for Claude child source tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from domain import (
    ids as domain_ids,
)
from harness.impl.claude_code.canonical.sources import (
    ClaudeRawEventSources,
    ClaudeTranscriptRawEventSource,
)
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture

SOURCES_WITH_TWO_CHILDREN = 5


@dataclass(frozen=True)
class ClaudeChildSourcesFixture:
    """Hold a parent session, source factory, and child transcript path."""

    session: Session
    factory: ClaudeRawEventSources
    child_path: Path


def claude_child_sources_fixture(tmp_path: Path) -> ClaudeChildSourcesFixture:
    """Write parent and child transcripts with child metadata.

    Returns:
        The session, source factory, and child transcript path.

    """
    parent_path = tmp_path / "projects" / "workspace" / fixture.SESSION_ONE_JSONL_PATH
    child_path = (
        tmp_path / "projects" / "workspace" / fixture.SESSION_ONE_ID / fixture.SUBAGENTS / "agent-child-one.jsonl"
    )
    child_path.parent.mkdir(parents=True)
    parent_path.write_text('{"type":"user","uuid":"parent"}\n')
    child_path.write_text('{"type":"user","uuid":"child"}\n')
    child_path.with_name("agent-child-one.meta.json").write_text("{}")
    return ClaudeChildSourcesFixture(
        Session(
            session_id=domain_ids.SessionId(fixture.SESSION_ONE_ID),
            lead_actor_id=domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
            source_reference=str(parent_path),
            working_directory=tmp_path.as_posix(),
        ),
        ClaudeRawEventSources(tmp_path.as_posix()),
        child_path,
    )


def assert_claude_child_source_context(
    child_source: ClaudeTranscriptRawEventSource,
) -> None:
    """Verify the child transcript source actor context."""
    assert child_source.context.actor_id == domain_ids.ActorId(fixture.CHILD_ONE_ID)
    assert child_source.context.parent_actor_id == domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID)


def assert_claude_child_source_refresh(
    source_fixture: ClaudeChildSourcesFixture,
    initial_sources: tuple[object, ...],
) -> None:
    """Verify that a new child transcript refreshes the source collection."""
    second_child = source_fixture.child_path.with_name("agent-child-two.jsonl")
    second_child.write_text('{"type":"user","uuid":"child-two"}\n')
    second_child.with_name("agent-child-two.meta.json").write_text("{}")

    refreshed = source_fixture.factory.for_session(source_fixture.session)
    assert refreshed is not initial_sources
    assert len(refreshed) == SOURCES_WITH_TWO_CHILDREN
