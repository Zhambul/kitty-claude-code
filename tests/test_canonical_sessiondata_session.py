# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata session."""

from __future__ import annotations

from dataclasses import replace

from tests import (
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_folding as folding,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain


def test_session_is_born_from_its_own_fact() -> None:
    """Verify a session is born from its own fact and nothing else.

    No `session.started`, no row. A usage report for a session nobody
        announced would otherwise put a nameless entry on the list.
    """
    report = session_domain.event_telemetry.UsageReported(
        scope=session_domain.usage.UsageScope.SESSION,
        subject_id="session-one",
        model=None,
        account=None,
        tokens=session_domain.usage.TokenUsage(1),
        cumulative=True,
        cost_in_usd=None,
    )
    assert folding.fold(report).session is None
    facts = folding.fold(
        replace(session_values.A_START, working_directory=session_values.WORKING_DIRECTORY),
    ).session
    assert facts is not None
    assert (facts.session_id, facts.state, facts.working_directory) == (
        session_values.SESSION,
        session_values.RUNNING_STATE,
        session_values.WORKING_DIRECTORY,
    )
    assert facts.lead_actor_id == session_values.LEAD


def test_title_person_chose_outranks_every_title() -> None:
    """Verify a title a person chose outranks every title a harness derived.

    Four sources name a session and they arrive in any order, so precedence
        cannot be "the last one wins" — it is what a person chose, then what the
        harness named, then a summary of it, then the first thing asked.
    """
    prompt = session_domain.event_conversation.MessageCreated(
        session_values.FIRST_MESSAGE_ID,
        session_domain.messaging.MessageRole.USER,
        session_domain.content.TextContent("Fix the reconnect bug"),
        session_domain.messaging.MessagePhase.PROMPT,
        None,
    )
    assert folding.session_after(*session_fixtures.alive(), prompt).title == "Fix the reconnect bug"
    assert (
        folding.session_after(
            *session_fixtures.alive(),
            prompt,
            session_domain.event_session.SessionTitleChanged(
                "Summarised", session_domain.work_state.TitleOrigin.SUMMARY,
            ),
        ).title
        == "Summarised"
    )
    assert (
        folding.session_after(
            *session_fixtures.alive(),
            session_domain.event_session.SessionTitleChanged(
                session_values.CHOSEN_ANSWER, session_domain.work_state.TitleOrigin.CUSTOM,
            ),
            session_domain.event_session.SessionTitleChanged(
                "Derived", session_domain.work_state.TitleOrigin.AUTOMATIC,
            ),
            prompt,
        ).title
        == session_values.CHOSEN_ANSWER
    )


def test_only_the_first_prompt_titles_a_session() -> None:
    """Verify only the first prompt titles a session."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_conversation.MessageCreated(
            session_values.FIRST_MESSAGE_ID,
            session_domain.messaging.MessageRole.USER,
            session_domain.content.TextContent("first ask"),
            session_domain.messaging.MessagePhase.PROMPT,
            None,
        ),
        session_domain.event_conversation.MessageCreated(
            session_domain.ids.MessageId("m2"),
            session_domain.messaging.MessageRole.USER,
            session_domain.content.TextContent("second ask"),
            session_domain.messaging.MessagePhase.PROMPT,
            None,
        ),
    )
    assert folding.session_from(state).title == "first ask"


def test_finished_session_says_when_and_resumed() -> None:
    """Verify a finished session says when and a resumed one keeps its work.

    A session that starts again is the same session: the lifecycle reopens and
        the title, goal and tasks it accumulated are still true.
    """
    finished = folding.session_after(
        *session_fixtures.alive(),
        session_domain.event_session.SessionTitleChanged(
            session_values.CHOSEN_ANSWER, session_domain.work_state.TitleOrigin.CUSTOM,
        ),
        session_domain.event_work.GoalChanged(
            session_values.SHIP_PROMPT, session_domain.work_state.GoalState.ACTIVE, None,
        ),
        folding.committed(
            session_domain.event_session.SessionFinished(session_domain.outcomes.Outcome.SUCCEEDED, None),
            cursor=9,
            occurred_at=session_values.SESSION_FINISH_TIME,
        ),
    )
    assert (finished.state, finished.finished_at) == (session_values.FINISHED_STATE, session_values.SESSION_FINISH_TIME)

    resumed = folding.session_after(
        *session_fixtures.alive(),
        session_domain.event_session.SessionTitleChanged(
            session_values.CHOSEN_ANSWER, session_domain.work_state.TitleOrigin.CUSTOM,
        ),
        session_domain.event_work.GoalChanged(
            session_values.SHIP_PROMPT, session_domain.work_state.GoalState.ACTIVE, None,
        ),
        session_domain.event_session.SessionFinished(session_domain.outcomes.Outcome.SUCCEEDED, None),
        session_fixtures.started(),
    )
    assert (resumed.state, resumed.finished_at) == (session_values.RUNNING_STATE, None)
    assert resumed.title == session_values.CHOSEN_ANSWER
    assert resumed.goal is not None
    assert resumed.goal.objective == session_values.SHIP_PROMPT


def test_an_account_is_the_last_one_reported() -> None:
    """Verify an account is the last one reported."""
    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_session.SessionTitleChanged("t", session_domain.work_state.TitleOrigin.CUSTOM),
    )
    assert folding.session_from(state).account is None
    state = folding.fold(*session_fixtures.alive(), session_fixtures.session_account_changed_fixture())
    account = folding.session_from(state).account
    assert account is not None
    assert account.display_name == "zhambyl"
