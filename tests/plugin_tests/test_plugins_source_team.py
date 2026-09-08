# Copyright (c) 2026 Zhambyl Yermagambet
"""Claude team source tests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from domain import (
    event_actor,
    event_conversation,
    ids as domain_ids,
)
from harness.impl.claude_code.canonical.sources import (
    ClaudeTeammateIdleRawEventSource,
)
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.source_team_support import TeamMessageCase, claude_team_message_audit

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.parametrize(
    "message_case",
    [
        TeamMessageCase(
            fixture.SESSION_ONE_LEAD_ID,
            None,
            fixture.WORKER_ONE_ID,
            fixture.WORKER_ONE_ID,
            domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
            starts_actor=True,
            expected_role="peer",
        ),
        TeamMessageCase(
            fixture.WORKER_ONE_ID,
            domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
            fixture.SESSION_ONE_LEAD_ID,
            fixture.SESSION_ONE_LEAD_ID,
            None,
            starts_actor=False,
            expected_role="peer",
        ),
        # The lead alias in a teammate transcript carries the teammate's brief.
        # The brief belongs to the child turn. It is not a second lead actor.
        TeamMessageCase(
            fixture.WORKER_ONE_ID,
            domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
            "team-lead",
            fixture.WORKER_ONE_ID,
            domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
            starts_actor=True,
            expected_role="parent",
        ),
    ],
)
def test_claude_team_messages_preserve_native(
    tmp_path: Path,
    message_case: TeamMessageCase,
) -> None:
    """Verify Claude team messages preserve the native sender as evidence actor.

    Raises:
        AssertionError: If the team message audit has no interpretation.

    """
    audit = claude_team_message_audit(tmp_path, message_case)

    assert audit.raw_event.actor_id == domain_ids.ActorId(message_case.expected_actor_id)
    assert audit.raw_event.parent_actor_id == message_case.expected_parent_actor_id
    interpretation = audit.interpretation
    if interpretation is None:
        msg = "team message audit has no interpretation"
        raise AssertionError(msg)
    assert all(
        recorded_event.event.actor_id == domain_ids.ActorId(message_case.expected_actor_id)
        for recorded_event in interpretation.events
    )
    assert (
        any(
            isinstance(recorded_event.event.payload, event_actor.ActorStarted)
            for recorded_event in interpretation.events
        )
        is message_case.starts_actor
    )
    message = next(
        recorded_event.event.payload
        for recorded_event in interpretation.events
        if isinstance(recorded_event.event.payload, event_conversation.MessageCreated)
    )
    assert message.role == message_case.expected_role


def test_claude_teammate_idle_source_splits(tmp_path: Path) -> None:
    """Verify claude teammate idle source splits and attributes each notification."""
    source_path = tmp_path / fixture.SESSION_ONE_JSONL_PATH
    child_directory = tmp_path / fixture.SESSION_ONE_ID / fixture.SUBAGENTS
    child_directory.mkdir(parents=True)
    (child_directory / "agent-actor-one.meta.json").write_text(
        json.dumps({fixture.NAME_FIELD: fixture.WORKER_ONE_ID}),
    )
    (child_directory / "agent-actor-two.meta.json").write_text(
        json.dumps({fixture.NAME_FIELD: "worker-two"}),
    )
    source_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.USER,
                fixture.MESSAGE_FIELD: {
                    fixture.CONTENT_FIELD: (
                        "Another Claude session sent a message:\n"
                        '<teammate-message teammate_id="worker-one">'
                        '{"type":"idle_notification","from":"worker-one",'
                        '"timestamp":"2026-08-25T00:00:00Z","idleReason":"available"}'
                        "</teammate-message>\n"
                        '<teammate-message teammate_id="worker-two">'
                        '{"type":"idle_notification","from":"worker-two",'
                        '"timestamp":"2026-08-25T00:00:01Z","idleReason":"failed",'
                        '"failureReason":"limit"}'
                        "</teammate-message>\n"
                        '<teammate-message teammate_id="worker-one">'
                        '{"type":"idle_notification","from":"worker-one",'
                        '"timestamp":"2026-08-25T00:00:02Z","idleReason":"available"}'
                        "</teammate-message>\n"
                        "This came from another Claude session."
                    ),
                },
            },
        )
        + "\n",
    )
    session = Session(
        domain_ids.SessionId(fixture.SESSION_ONE_ID),
        domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID),
        source_path.as_posix(),
        fixture.WORK_PATH,
    )

    source = ClaudeTeammateIdleRawEventSource(session.source_context)
    raw_events = source.read(None)

    assert [event.actor_id for event in raw_events] == [
        domain_ids.ActorId("actor-one"),
        domain_ids.ActorId("actor-two"),
    ]
    assert all(event.parent_actor_id == domain_ids.ActorId(fixture.SESSION_ONE_LEAD_ID) for event in raw_events)
    assert len({event.raw_event_id for event in raw_events}) == len(raw_events)
    assert source.read(None) == ()
