# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata status basic."""

from __future__ import annotations

import pytest

from tests import canonical_sessiondata_fixtures as session_fixtures, canonical_sessiondata_values as session_values
from tests.canonical_sessiondata_components import domain as session_domain


def test_started_session_is_idle_and_finished_one() -> None:
    """Verify a started session is idle and a finished one shows no state."""
    assert session_fixtures.status_after() == "idle"
    assert (
        session_fixtures.status_after(
            session_domain.event_session.SessionFinished(session_domain.outcomes.Outcome.SUCCEEDED, None),
        )
        is None
    )


def test_prompt_or_turn_start_is_thinking() -> None:
    """Verify a prompt or a turn start is thinking and reasoning is working."""
    assert session_fixtures.status_after(session_domain.event_conversation.TurnStarted(None)) == "thinking"
    assert (
        session_fixtures.status_after(
            session_domain.event_conversation.MessageCreated(
                session_values.FIRST_MESSAGE_ID,
                session_domain.messaging.MessageRole.USER,
                session_domain.content.TextContent(session_values.GO_PROMPT),
                session_domain.messaging.MessagePhase.PROMPT,
                None,
            ),
        )
        == "thinking"
    )
    assert (
        session_fixtures.status_after(
            session_domain.event_conversation.ReasoningCreated(
                session_domain.ids.ReasoningId("r1"),
                session_domain.content.TextContent("hmm"),
            ),
        )
        == session_values.WORKING_STATE
    )


def test_an_assistant_message_is_not_a_prompt() -> None:
    """Verify an assistant message is not a prompt."""
    assert (
        session_fixtures.status_after(
            session_domain.event_conversation.MessageCreated(
                session_values.FIRST_MESSAGE_ID,
                session_domain.messaging.MessageRole.ASSISTANT,
                session_domain.content.TextContent("done"),
                session_domain.messaging.MessagePhase.END_TURN,
                None,
            ),
        )
        == "idle"
    )


@pytest.mark.parametrize(
    "payload",
    [
        session_domain.event_shell.ShellStarted(
            session_values.PRIMARY_SHELL_ID,
            session_values.SHELL_COMMAND_CONTENT,
            session_domain.outcomes.ExecutionMode.FOREGROUND,
            None,
        ),
        session_domain.event_resource.SkillStarted(session_domain.ids.SkillId("k1"), "audit-debug", None),
        session_domain.event_work.TaskChanged(
            session_values.FIRST_TASK_ID,
            session_values.FIRST_TASK_TEXT,
            None,
            session_domain.work_state.TaskState.IN_PROGRESS,
            session_values.LEAD,
        ),
        session_domain.event_work.TaskListChanged(session_values.TASK_LIST_ID, (session_values.FIRST_TASK_ID,)),
    ],
)
def test_work_being_done_is_executing(payload: session_domain.event_base.EventPayload) -> None:
    """Verify work being done is executing.

    A task tool is work, the same as a command — which is what the `task`
        category set before the categories dissolved.
    """
    assert session_fixtures.status_after(payload) == session_values.EXECUTING_STATE


@pytest.mark.parametrize(
    "payload",
    [
        session_domain.event_shell.ShellFinished(
            session_values.PRIMARY_SHELL_ID,
            session_domain.outcomes.Outcome.SUCCEEDED,
            None,
            0,
        ),
        session_domain.event_resource.FileAccessed(
            session_values.UPDATED_FILE_PATH,
            session_domain.outcomes.FileAction.UPDATED,
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
        session_domain.event_resource.SearchPerformed(
            "Grep",
            session_domain.content.TextContent("q"),
            None,
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
        session_domain.event_resource.WebFetched("https://x.dev", None, session_domain.outcomes.Outcome.SUCCEEDED),
        session_domain.event_resource.BrowserInteracted(
            "Refresh the fixture",
            session_domain.content.TextContent("snapshot"),
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
    ],
)
def test_work_that_ended_is_working_again(payload: session_domain.event_base.EventPayload) -> None:
    """Verify work that ended is working again."""
    assert (
        session_fixtures.status_after(
            session_domain.event_conversation.TurnStarted(None),
            session_domain.event_shell.ShellStarted(
                session_values.PRIMARY_SHELL_ID,
                session_values.SHELL_COMMAND_CONTENT,
                session_domain.outcomes.ExecutionMode.FOREGROUND,
                None,
            ),
            payload,
        )
        == session_values.WORKING_STATE
    )


def test_late_command_finish_does_not_reopen() -> None:
    """Verify a late command finish does not reopen an ended turn."""
    assert (
        session_fixtures.status_after(
            session_domain.event_conversation.TurnStarted(None),
            session_domain.event_shell.ShellStarted(
                session_values.PRIMARY_SHELL_ID,
                session_values.SHELL_COMMAND_CONTENT,
                session_domain.outcomes.ExecutionMode.FOREGROUND,
                None,
            ),
            session_fixtures.succeeded_turn(),
            session_domain.event_shell.ShellFinished(
                session_values.PRIMARY_SHELL_ID,
                session_domain.outcomes.Outcome.SUCCEEDED,
                None,
                0,
            ),
        )
        == session_values.AWAITING_RESPONSE_STATE
    )
