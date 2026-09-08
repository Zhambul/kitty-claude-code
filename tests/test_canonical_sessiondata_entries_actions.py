# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata entries actions."""

from __future__ import annotations

from tests import (
    canonical_sessiondata_actor_access as actor_access,
    canonical_sessiondata_entry_support as entry_support,
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_folding as folding,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain


def test_shell_finish_carries_three_states() -> None:
    """Verify a shell finish carries three states and the exit code where there is one."""
    assert entry_support.required_entry(
        session_domain.event_shell.ShellFinished(
            session_values.TERMINAL_SHELL_ID,
            session_domain.outcomes.Outcome.SUCCEEDED,
            None,
            0,
        ),
    ).body == session_domain.entry_shells.ShellFinishedBody(
        session_values.TERMINAL_SHELL_ID,
        session_domain.entry_base.RunState.SUCCEEDED,
        0,
    )
    assert entry_support.required_entry(
        session_domain.event_shell.ShellFinished(
            session_values.TERMINAL_SHELL_ID,
            session_domain.outcomes.Outcome.REJECTED,
            None,
            None,
        ),
    ).body == session_domain.entry_shells.ShellFinishedBody(
        session_values.TERMINAL_SHELL_ID,
        session_domain.entry_base.RunState.FAILED,
        None,
    )
    assert entry_support.required_entry(
        session_domain.event_shell.ShellFinished(
            session_values.TERMINAL_SHELL_ID,
            session_domain.outcomes.Outcome.CANCELLED,
            None,
            None,
        ),
    ).body == session_domain.entry_shells.ShellFinishedBody(
        session_values.TERMINAL_SHELL_ID,
        session_domain.entry_base.RunState.CANCELLED,
        None,
    )


def test_changed_file_is_shown_as_its_diff() -> None:
    """Verify a changed file is shown as its diff and a read one as its text."""
    changed = entry_support.required_entry(
        session_domain.event_resource.FileAccessed(
            session_values.UPDATED_FILE_PATH,
            session_domain.outcomes.FileAction.UPDATED,
            session_domain.outcomes.Outcome.SUCCEEDED,
            lines_added=1,
            lines_removed=1,
            unified_diff="@@ -1 +1 @@\n-a\n+b\n",
            content=session_domain.content.TextContent("the whole file"),
        ),
    )
    assert isinstance(changed.body, session_domain.entry_resources.FileBody)
    assert isinstance(changed.body.content, session_domain.content.TextContent)
    assert changed.body.content.text == "@@ -1 +1 @@\n-a\n+b\n"
    read = entry_support.required_entry(
        session_domain.event_resource.FileAccessed(
            session_values.UPDATED_FILE_PATH,
            session_domain.outcomes.FileAction.READ,
            session_domain.outcomes.Outcome.SUCCEEDED,
            content=session_domain.content.TextContent("print(1)"),
        ),
    )
    assert read.body == session_domain.entry_resources.FileBody(
        session_values.UPDATED_FILE_PATH,
        session_domain.outcomes.FileAction.READ,
        session_domain.entry_base.FileState.SUCCEEDED,
        None,
        None,
        None,
        session_domain.content.TextContent("print(1)"),
    )


def test_turn_marker_carries_nothing_and_its_end() -> None:
    """Verify a turn marker carries nothing and its end carries how it ended."""
    assert (
        entry_support.required_entry(
            session_domain.event_conversation.TurnStarted(session_values.FIRST_MESSAGE_ID),
        ).entry_type
        == "turn_started"
    )
    assert entry_support.required_entry(
        session_fixtures.succeeded_turn(),
    ).body == session_domain.entry_conversation.TurnFinishedBody(session_domain.entry_base.TurnState.FINISHED)
    assert entry_support.required_entry(
        session_domain.event_conversation.TurnAborted(None),
    ).body == session_domain.entry_conversation.TurnFinishedBody(session_domain.entry_base.TurnState.ABORTED)


def test_question_entry_keeps_choices_person() -> None:
    """Verify a question entry keeps the choices a person is offered."""
    asked = session_domain.event_work.QuestionAsked(
        session_domain.ids.AttentionId("att-3"),
        (
            session_domain.attention.AttentionPrompt(
                prompt_id=session_domain.ids.QuestionId("q1"),
                title=None,
                prompt="Allow Bash?",
                multiple=False,
                choices=(session_domain.attention.AttentionChoice("Yes", None),),
            ),
        ),
    )
    assert entry_support.required_entry(asked).body == session_domain.entry_attention.QuestionAskedBody(
        session_domain.ids.AttentionId("att-3"), asked.questions,
    )


def test_model_change_entry_marks_fallback() -> None:
    """Verify a model change entry marks a fallback the harness chose for you."""
    automatic = entry_support.required_entry(
        session_domain.event_session.ModelChanged(
            session_domain.references.ModelReference(session_values.OPUS_MODEL_ID, session_values.OPUS_MODEL_NAME),
            session_domain.references.ModelReference("claude-fable-5", "Fable 5"),
            session_domain.work_state.ModelChangeReason.AUTOMATIC_FALLBACK,
        ),
    )
    assert automatic.body == session_domain.entry_lifecycle.ModelChangeBody(
        current="Fable 5", previous=session_values.OPUS_MODEL_NAME, automatic=True,
    )


def test_only_a_real_switch_reaches_the_feed() -> None:
    """Verify only a real switch reaches the feed.

    Four facts a launch produces, and how many lines a reader should see: one,
        and only if they actually switched something.

        Measured on a live session (b29af821): the feed showed "model sonnet",
        "effort low", "model sonnet → sonnet-5" and "effort low" again, for a person
        who had chosen sonnet at low effort exactly once. Every one of those is a
        report, not a change. The fourth was not even the same actor — a subagent
        reporting its own effort three seconds later, which is per-actor state
        landing on a per-actor row and correct; it drew a line only because a report
        used to draw one.
    """
    launched = session_domain.references.ModelReference(session_values.SONNET_MODEL_ID, session_values.SONNET_MODEL_ID)
    resolved = session_domain.references.ModelReference("claude-sonnet-5", session_values.SONNET_MODEL_NAME)

    # An initial report is not a change: nothing it replaced is known, which is
    # what `previous is None` means.
    # …and the same value again, from the harness's own stream, is not either.
    assert (
        entry_support.body_of(
            session_domain.event_session.ModelChanged(
                None, launched, session_domain.work_state.ModelChangeReason.SELECTED,
            ),
        ),
        entry_support.body_of(
            session_domain.event_session.EffortChanged(
                None, session_values.LOW_EFFORT, session_domain.work_state.EffortChangeReason.SELECTED,
            ),
        ),
        entry_support.body_of(
            session_domain.event_session.EffortChanged(
                session_values.LOW_EFFORT,
                session_values.LOW_EFFORT,
                session_domain.work_state.EffortChangeReason.REPORTED_BY_HARNESS,
            ),
        ),
    ) == (None, None, None)

    # Alias refinement is suppressed by the adapter before this layer; the
    # canonical reader deliberately has no vendor alias vocabulary.
    # …but the actor's row takes the better name, because that is what an
    # aggregate is for. The refinement lands; only the feed line goes.
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_session.ModelChanged(None, launched, session_domain.work_state.ModelChangeReason.SELECTED),
        session_domain.event_session.ModelChanged(
            launched, resolved, session_domain.work_state.ModelChangeReason.REPORTED_BY_HARNESS,
        ),
    )
    assert actor_access.lead_model(state) == resolved

    # A person switching models IS a change: a different selection.
    assert entry_support.body_of(
        session_domain.event_session.ModelChanged(
            resolved,
            session_domain.references.ModelReference(session_values.OPUS_MODEL_ID, session_values.OPUS_MODEL_NAME),
            session_domain.work_state.ModelChangeReason.SELECTED,
        ),
    ) == session_domain.entry_lifecycle.ModelChangeBody(
        current=session_values.OPUS_MODEL_NAME,
        previous=session_values.SONNET_MODEL_NAME,
        automatic=False,
    )
    # So is a fallback the harness chose, and it says so.
    assert entry_support.body_of(
        session_domain.event_session.ModelChanged(
            resolved,
            session_domain.references.ModelReference("claude-haiku-4-5", "haiku"),
            session_domain.work_state.ModelChangeReason.AUTOMATIC_FALLBACK,
        ),
    ) == session_domain.entry_lifecycle.ModelChangeBody(
        current="haiku", previous=session_values.SONNET_MODEL_NAME, automatic=True,
    )
    # And so is a real effort switch.
    assert entry_support.body_of(
        session_domain.event_session.EffortChanged(
            session_values.LOW_EFFORT,
            session_values.HIGH_EFFORT,
            session_domain.work_state.EffortChangeReason.SELECTED,
        ),
    ) == session_domain.entry_lifecycle.EffortChangeBody(session_values.HIGH_EFFORT, session_values.LOW_EFFORT)


def test_assignment_entry_carries_brief_as_its() -> None:
    """Verify an assignment entry carries the brief as its summary."""
    entry = entry_support.required_entry(
        session_domain.event_actor.ActorAssignmentStarted(
            session_values.FIRST_ASSIGNMENT_ID,
            session_domain.content.TextContent("Get the weather"),
            actor_name=session_values.EXPLORE_TASK_TEXT,
            prompt=session_domain.content.TextContent("look it up"),
        ),
    )
    assert entry.summary == "Get the weather"
    assert entry.body == session_domain.entry_lifecycle.AssignmentStartedBody(
        session_values.FIRST_ASSIGNMENT_ID,
        session_values.EXPLORE_TASK_TEXT,
        session_domain.content.TextContent("look it up"),
    )
