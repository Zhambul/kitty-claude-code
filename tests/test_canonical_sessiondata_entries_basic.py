# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata entries basic."""

from __future__ import annotations

import pytest

from tests import canonical_sessiondata_entry_support as entry_support, canonical_sessiondata_values as session_values
from tests.canonical_sessiondata_components import domain as session_domain


def test_entry_carries_envelope_client_joins() -> None:
    """Verify an entry carries the envelope the client joins on.

    The envelope is the join: a client resolves the actor's name and colour
        from `SessionData.actors`, groups by the turn, and orders by the cursor — so
        an entry that dropped any of them would need the canonical log to be read.
    """
    entry = entry_support.required_entry(
        session_domain.event_conversation.MessageCreated(
            session_values.FIRST_MESSAGE_ID,
            session_domain.messaging.MessageRole.ASSISTANT,
            session_domain.content.TextContent("hi"),
            session_domain.messaging.MessagePhase.END_TURN,
            None,
        ),
        actor_id=session_values.CHILD,
        parent_actor_id=session_values.LEAD,
        turn_id=session_domain.ids.TurnId("turn-7"),
        occurred_at=session_values.ENTRY_OCCURRED_AT,
        event_id="event-abc",
    )
    assert (entry.entry_id, entry.turn_id) == (
        session_domain.ids.CanonicalEventId("event-abc"),
        session_domain.ids.TurnId("turn-7"),
    )
    assert (entry.actor_id, entry.parent_actor_id) == (session_values.CHILD, session_values.LEAD)
    assert entry.occurred_at == pytest.approx(session_values.ENTRY_OCCURRED_AT)
    assert entry.entry_type == session_values.MESSAGE_ENTRY_TYPE
    assert entry.body == session_domain.entry_conversation.MessageBody(
        session_values.FIRST_MESSAGE_ID,
        session_domain.messaging.MessageRole.ASSISTANT,
        session_domain.messaging.MessagePhase.END_TURN,
        session_domain.content.TextContent("hi"),
        None,
    )


def test_actor_to_actor_message_is_message() -> None:
    """Verify an actor to actor message is a message with a recipient."""
    entry = entry_support.required_entry(
        session_domain.event_conversation.MessageCreated(
            session_values.FIRST_MESSAGE_ID,
            session_domain.messaging.MessageRole.ASSISTANT,
            session_domain.content.TextContent(session_values.GO_PROMPT),
            session_domain.messaging.MessagePhase.INTERMEDIATE,
            None,
            session_values.CHILD,
        ),
    )
    assert isinstance(entry.body, session_domain.entry_conversation.MessageBody)
    assert entry.body.recipient_actor_id == session_values.CHILD


def test_finished_compaction_entry_carries() -> None:
    """Verify a finished compaction entry carries expandable context."""
    context = session_domain.content.TextContent("The retained compacted context")
    entry = entry_support.required_entry(
        session_domain.event_telemetry.CompactionFinished(
            session_values.CONTEXT_USED_TOKENS, session_values.COMPACTION_RESULT_TOKENS, context,
        ),
    )

    assert entry.body == session_domain.entry_lifecycle.CompactionFinishedBody(
        session_values.CONTEXT_USED_TOKENS, session_values.COMPACTION_RESULT_TOKENS, context,
    )


def test_browser_entry_keeps_its_title() -> None:
    """Verify a browser entry keeps its title and expandable result."""
    result = session_domain.content.TextContent('- banner:\n  - link "baqylau"')
    entry = entry_support.required_entry(
        session_domain.event_resource.BrowserInteracted(
            "Refresh the fixture application",
            result,
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
    )

    assert entry.entry_type == "browser"
    assert entry.body == session_domain.entry_resources.BrowserBody(
        "Refresh the fixture application",
        session_domain.entry_base.FileState.SUCCEEDED,
        result,
    )


@pytest.mark.parametrize(
    "payload",
    [
        session_domain.event_session.SessionStarted(
            session_values.WORKING_DIRECTORY, "ref", None, None, None, None, None,
        ),
        session_domain.event_actor.ActorStarted(
            session_values.CLAUDE_ACTOR_NAME, session_domain.messaging.ActorRole.LEAD,
        ),
        session_domain.event_actor.ActorFinished(None),
        session_domain.event_work.TaskChanged(
            session_values.FIRST_TASK_ID,
            session_values.FIRST_TASK_TEXT,
            None,
            session_domain.work_state.TaskState.PENDING,
            None,
        ),
        session_domain.event_work.TaskListChanged(session_values.TASK_LIST_ID, ()),
        session_domain.event_work.GoalChanged(
            session_values.SHIP_PROMPT, session_domain.work_state.GoalState.ACTIVE, None,
        ),
        session_domain.event_telemetry.UsageReported(
            scope=session_domain.usage.UsageScope.ACTOR,
            subject_id=session_values.LEAD_ACTOR_LABEL,
            model=None,
            account=None,
            tokens=session_domain.usage.TokenUsage(1),
            cumulative=True,
            cost_in_usd=None,
        ),
        session_domain.event_telemetry.ContextReported(1, 2, None),
        session_domain.event_shell.ShellOutputLocated(
            shell_id=session_values.PRIMARY_SHELL_ID,
            source_path="/test-data/output",
            chunk_source_type="chunk",
            delete_source=False,
            initial_size=0,
            initial_modified_at=0,
            wait_for_source_change=False,
            until=session_domain.work_state.ShellFollowUntil.SHELL_FINISHED,
        ),
    ],
)
def test_plumbing_and_aggregate_facts_produce_no(
    payload: session_domain.event_base.EventPayload,
) -> None:
    """Verify plumbing and aggregate facts produce no entry.

    A feed that showed these would be showing machinery: they feed the
        aggregate, where the current value is the whole truth.
    """
    assert entry_support.entry_of(payload) is None


def test_shell_entry_carries_command_and_harness() -> None:
    """Verify a shell entry carries the command and the harness description as its summary."""
    entry = entry_support.required_entry(
        session_domain.event_shell.ShellStarted(
            session_values.TERMINAL_SHELL_ID,
            session_values.SHELL_COMMAND_CONTENT,
            session_domain.outcomes.ExecutionMode.FOREGROUND,
            "Run the tests",
        ),
    )
    assert entry.summary == "Run the tests"
    assert entry.body == session_domain.entry_shells.ShellStartedBody(
        session_values.TERMINAL_SHELL_ID,
        session_values.SHELL_COMMAND_CONTENT,
        session_domain.outcomes.ExecutionMode.FOREGROUND,
    )


def test_output_arrives_as_immutable_chunks() -> None:
    """Verify output arrives as immutable chunks for the client to fold."""
    entry = entry_support.required_entry(
        session_domain.event_shell.ShellProgressed(
            session_values.TERMINAL_SHELL_ID,
            0,
            session_domain.outcomes.ProgressStream.OUTPUT,
            session_domain.content.TextContent("142 passed\n"),
            session_domain.outcomes.OutputMode.APPEND,
        ),
    )
    assert entry.body == session_domain.entry_shells.ShellOutputBody(
        session_values.TERMINAL_SHELL_ID,
        session_domain.outcomes.ProgressStream.OUTPUT,
        session_domain.outcomes.OutputMode.APPEND,
        session_domain.content.TextContent("142 passed\n"),
    )
