# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata usage."""

from __future__ import annotations

from decimal import Decimal

import pytest

from tests import (
    canonical_sessiondata_actor_access as actor_access,
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_folding as folding,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain

DISTINCT_FILE_COUNT = 2


def test_cumulative_usage_report_replaces() -> None:
    """Verify a cumulative usage report replaces and a share adds up.

    A harness says which it is sending, and treating a total as a share is how
        a session's cost silently doubles.
    """
    replaced = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_telemetry.UsageReported(
            scope=session_domain.usage.UsageScope.ACTOR,
            subject_id=session_values.LEAD_ACTOR_LABEL,
            model=None,
            account=None,
            tokens=session_domain.usage.TokenUsage(input_tokens=10),
            cumulative=True,
            cost_in_usd=Decimal("1.00"),
        ),
        session_domain.event_telemetry.UsageReported(
            scope=session_domain.usage.UsageScope.ACTOR,
            subject_id=session_values.LEAD_ACTOR_LABEL,
            model=None,
            account=None,
            tokens=session_domain.usage.TokenUsage(input_tokens=session_values.REPLACEMENT_INPUT_TOKENS),
            cumulative=True,
            cost_in_usd=Decimal("3.00"),
        ),
    )
    assert folding.actor_from(replaced).usage.tokens.input_tokens == session_values.REPLACEMENT_INPUT_TOKENS
    assert folding.actor_from(replaced).usage.cost_in_usd == Decimal("3.00")

    added = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_telemetry.UsageReported(
            scope=session_domain.usage.UsageScope.ACTOR,
            subject_id=session_values.LEAD_ACTOR_LABEL,
            model=None,
            account=None,
            tokens=session_domain.usage.TokenUsage(input_tokens=10),
            cumulative=False,
            cost_in_usd=Decimal("1.00"),
        ),
        session_domain.event_telemetry.UsageReported(
            scope=session_domain.usage.UsageScope.ACTOR,
            subject_id=session_values.LEAD_ACTOR_LABEL,
            model=None,
            account=None,
            tokens=session_domain.usage.TokenUsage(input_tokens=session_values.REPLACEMENT_INPUT_TOKENS),
            cumulative=False,
            cost_in_usd=Decimal("3.00"),
        ),
    )
    assert folding.actor_from(added).usage.tokens.input_tokens == session_values.COMBINED_INPUT_TOKENS
    assert folding.actor_from(added).usage.cost_in_usd == Decimal("4.00")


def test_context_window_reports_its_fill_and_says() -> None:
    """Verify the context window reports its fill and says when it is being emptied."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_telemetry.ContextReported(
            session_values.CONTEXT_USED_TOKENS, session_values.CONTEXT_WINDOW_TOKENS, None,
        ),
        session_domain.event_telemetry.CompactionStarted(session_values.CONTEXT_USED_TOKENS),
    )
    context = actor_access.lead_context(state)
    assert context.used_tokens == session_values.CONTEXT_USED_TOKENS
    assert context.window_tokens == session_values.CONTEXT_WINDOW_TOKENS
    assert context.compacting is True

    compacted = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_telemetry.ContextReported(
            session_values.CONTEXT_USED_TOKENS, session_values.CONTEXT_WINDOW_TOKENS, None,
        ),
        session_domain.event_telemetry.CompactionStarted(session_values.CONTEXT_USED_TOKENS),
        session_domain.event_telemetry.CompactionFinished(
            session_values.CONTEXT_USED_TOKENS, session_values.COMPACTION_RESULT_TOKENS,
        ),
    )
    assert folding.actor_from(compacted).context.compacting is False
    assert folding.actor_from(compacted).context.used_tokens == session_values.COMPACTION_RESULT_TOKENS


def test_scoreboard_counts_distinct_files() -> None:
    """Verify the scoreboard counts distinct files and names a tool per action."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_resource.FileAccessed(
            session_values.UPDATED_FILE_PATH,
            session_domain.outcomes.FileAction.UPDATED,
            session_domain.outcomes.Outcome.SUCCEEDED,
            lines_added=session_values.UPDATED_FILE_LINE_COUNT,
            lines_removed=3,
        ),
        session_domain.event_resource.FileAccessed(
            session_values.UPDATED_FILE_PATH,
            session_domain.outcomes.FileAction.UPDATED,
            session_domain.outcomes.Outcome.SUCCEEDED,
            lines_added=1,
            lines_removed=0,
        ),
        session_domain.event_resource.FileAccessed(
            "/work/b.py",
            session_domain.outcomes.FileAction.READ,
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
        session_domain.event_resource.SearchPerformed(
            "Grep",
            session_domain.content.TextContent("shell_id"),
            None,
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
        session_domain.event_resource.WebFetched("https://x.dev", None, session_domain.outcomes.Outcome.SUCCEEDED),
        session_domain.event_resource.BrowserInteracted(
            "Refresh the fixture",
            session_domain.content.TextContent("snapshot"),
            session_domain.outcomes.Outcome.SUCCEEDED,
        ),
    )
    statistics = actor_access.lead_statistics(state)
    assert statistics.file_count == DISTINCT_FILE_COUNT
    assert (statistics.lines_added, statistics.lines_removed) == (13, 3)
    assert statistics.tool_counts == (
        session_domain.actor_state.ToolCount("Browser", 1),
        session_domain.actor_state.ToolCount("Edit", 2),
        session_domain.actor_state.ToolCount("Grep", 1),
        session_domain.actor_state.ToolCount("Read", 1),
        session_domain.actor_state.ToolCount("WebFetch", 1),
    )


def test_commands_are_counted_once_and_their() -> None:
    """Verify commands are counted once and their failures separately."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_shell.ShellStarted(
            session_values.PRIMARY_SHELL_ID,
            session_values.SHELL_COMMAND_CONTENT,
            session_domain.outcomes.ExecutionMode.FOREGROUND,
            None,
        ),
        session_domain.event_shell.ShellFinished(
            session_values.PRIMARY_SHELL_ID,
            session_domain.outcomes.Outcome.FAILED,
            None,
            1,
        ),
        session_domain.event_shell.ShellStarted(
            session_domain.ids.ShellId("sh2"),
            session_domain.content.TextContent("make lint"),
            session_domain.outcomes.ExecutionMode.FOREGROUND,
            None,
        ),
        session_domain.event_shell.ShellFinished(
            session_domain.ids.ShellId("sh2"),
            session_domain.outcomes.Outcome.SUCCEEDED,
            None,
            0,
        ),
    )
    statistics = actor_access.lead_statistics(state)
    assert (statistics.shell_command_count, statistics.failed_shell_command_count) == (2, 1)
    # A command is not a "tool" on the counts row: it is already the row above.
    assert statistics.tool_counts == ()


def test_prompts_and_actor_messages_are_counted() -> None:
    """Verify prompts and actor messages are counted apart."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_conversation.MessageCreated(
            session_values.FIRST_MESSAGE_ID,
            session_domain.messaging.MessageRole.USER,
            session_domain.content.TextContent(session_values.GO_PROMPT),
            session_domain.messaging.MessagePhase.PROMPT,
            None,
        ),
        session_domain.event_conversation.MessageCreated(
            session_domain.ids.MessageId("m2"),
            session_domain.messaging.MessageRole.ASSISTANT,
            session_domain.content.TextContent("ok"),
            session_domain.messaging.MessagePhase.INTERMEDIATE,
            None,
            session_values.CHILD,
        ),
    )
    statistics = actor_access.lead_statistics(state)
    assert (statistics.prompt_count, statistics.actor_message_count) == (1, 1)


def test_active_seconds_measures_closed_intervals() -> None:
    """Verify active seconds measures closed intervals and leaves the open one to the reader.

    A number that grows on its own cannot be a stored fact — writing a row per
        second is the alternative. The interval still open is added when somebody
        asks, so what is stored is only what has definitely elapsed.
    """
    state = folding.fold(
        folding.committed(session_fixtures.started(), cursor=1, occurred_at=100.0),
        folding.committed(
            session_domain.event_actor.ActorStarted(
                session_values.CLAUDE_ACTOR_NAME, session_domain.messaging.ActorRole.LEAD,
            ),
            cursor=2,
            occurred_at=100.0,
        ),
        folding.committed(
            session_fixtures.succeeded_turn(),
            cursor=3,
            occurred_at=session_values.FIRST_TURN_FINISH_TIME,
        ),
        folding.committed(
            session_domain.event_conversation.MessageCreated(
                session_values.FIRST_MESSAGE_ID,
                session_domain.messaging.MessageRole.USER,
                session_domain.content.TextContent("again"),
                session_domain.messaging.MessagePhase.PROMPT,
                None,
            ),
            cursor=4,
            occurred_at=session_values.SECOND_TURN_START_TIME,
        ),
    )
    statistics = actor_access.lead_statistics(state)
    assert statistics.active_seconds == pytest.approx(session_values.FIRST_ACTIVE_INTERVAL_SECONDS)
    assert statistics.active_since_internal == pytest.approx(session_values.SECOND_TURN_START_TIME)


def test_fact_with_no_clock_of_its_own_is_timed() -> None:
    """Verify a fact with no clock of its own is timed by when we recorded it.

    `occurred_at` is nullable by design, and a fold that measured on the bare
        column would be subtracting None.
    """
    state = folding.fold(
        folding.committed(session_fixtures.started(), cursor=1, accepted_at=100.0),
        folding.committed(
            session_domain.event_actor.ActorStarted(
                session_values.CLAUDE_ACTOR_NAME, session_domain.messaging.ActorRole.LEAD,
            ),
            cursor=2,
            accepted_at=100.0,
        ),
        folding.committed(
            session_fixtures.succeeded_turn(),
            cursor=3,
            accepted_at=session_values.ACCEPTED_TURN_FINISH_TIME,
        ),
    )
    assert actor_access.lead_statistics(state).active_seconds == pytest.approx(
        session_values.ACCEPTED_ACTIVE_INTERVAL_SECONDS,
    )
