# Copyright (c) 2026 Zhambyl Yermagambet
"""Assert exact changes between two application insight snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit import insight_session, insight_values

if TYPE_CHECKING:
    from api.application.models.insights.application_insights_response import (
        ApplicationInsightsResponse,
        InsightWindowResponse,
        ProjectInsightsResponse,
    )
    from sdk.state import SessionSnapshot


def assert_completed_session_delta(
    before: ApplicationInsightsResponse,
    after: ApplicationInsightsResponse,
    session: SessionSnapshot,
) -> None:
    """Verify insights changed by exactly one completed session."""
    delta = insight_session.completed_session_delta(session)
    assert_insight_totals(before, after, delta)
    assert_project_delta(before, after, delta)


def assert_insight_totals(
    before: ApplicationInsightsResponse,
    after: ApplicationInsightsResponse,
    delta: insight_session.CompletedSessionDelta,
) -> None:
    """Verify aggregate insight totals."""
    assert after.generated_at >= before.generated_at
    assert after.total_session_count == before.total_session_count + 1
    assert insight_values.daily_count(after.daily_sessions, delta.started.date()) == (
        insight_values.daily_count(before.daily_sessions, delta.started.date()) + 1
    )
    assert insight_values.hourly_count(after.hourly_sessions, delta.started) == (
        insight_values.hourly_count(before.hourly_sessions, delta.started) + 1
    )
    for before_window, after_window in (
        (before.last_seven_days, after.last_seven_days),
        (before.last_thirty_days, after.last_thirty_days),
        (before.all_time, after.all_time),
    ):
        assert_window_delta(before_window, after_window, delta)


def assert_project_delta(
    before: ApplicationInsightsResponse,
    after: ApplicationInsightsResponse,
    delta: insight_session.CompletedSessionDelta,
) -> None:
    """Verify the completed session changed its project summary."""
    before_project = insight_values.project(before, delta.working_directory)
    after_project = insight_values.project(after, delta.working_directory)
    assert after_project is not None, f"insights have no project {delta.working_directory!r}"
    assert_project_counts(before_project, after_project, delta)
    insight_values.assert_float_delta(
        insight_values.project_value(before_project, "cost_in_usd"),
        after_project.cost_in_usd,
        delta.cost_in_usd,
    )
    assert (after_project.error_count, after_project.last_session_at) == (
        insight_values.project_value(before_project, "error_count"),
        delta.started_at,
    )
    before_daily_sessions = () if before_project is None else before_project.daily_sessions
    assert insight_values.daily_count(after_project.daily_sessions, delta.started.date()) == (
        insight_values.daily_count(before_daily_sessions, delta.started.date()) + 1
    )


def assert_project_counts(
    before_project: ProjectInsightsResponse | None,
    after_project: ProjectInsightsResponse,
    delta: insight_session.CompletedSessionDelta,
) -> None:
    """Verify project session and token counts."""
    assert after_project.session_count == insight_values.project_value(before_project, "session_count") + 1
    assert after_project.token_count == insight_values.project_value(before_project, "token_count") + delta.token_count


def assert_window_delta(
    before: InsightWindowResponse,
    after: InsightWindowResponse,
    delta: insight_session.CompletedSessionDelta,
) -> None:
    """Verify one insight window changed by the completed session."""
    assert_window_session_counts(before, after)
    assert after.token_count == before.token_count + delta.token_count
    insight_values.assert_float_delta(before.cost_in_usd, after.cost_in_usd, delta.cost_in_usd)
    assert after.error_count == before.error_count
    assert insight_values.project_summary_count(after.projects, delta.working_directory) == (
        insight_values.project_summary_count(before.projects, delta.working_directory) + 1
    )


def assert_window_session_counts(before: InsightWindowResponse, after: InsightWindowResponse) -> None:
    """Verify session counters in one insight window."""
    assert after.session_count == before.session_count + 1
    assert after.active_session_count == before.active_session_count
    assert after.finished_session_count == before.finished_session_count + 1
