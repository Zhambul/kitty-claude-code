# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that read and check application insights."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit.insights import assert_completed_session_delta

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.observation_contexts import InsightSessionContext
    from tests.e2e.testkit.references import InsightsSnapshots


@when(parsers.parse('I read application insights as "{name}"'))
def read_application_insights(client: BaqylauClient, insights_snapshots: InsightsSnapshots, name: str) -> None:
    """Read and name the application insights."""
    insights_snapshots.bind(name, client.insights.state())


@then(parsers.parse('insights "{name}" include the workspace'))
def insights_include_workspace(insights_snapshots: InsightsSnapshots, workspace: str, name: str) -> None:
    """Verify insights include the workspace."""
    found = [
        project_insight
        for project_insight in insights_snapshots.get(name).projects
        if project_insight.working_directory == workspace
    ]
    assert len(found) == 1, f"insights {name!r} have {len(found)} workspace rows"


@then(parsers.parse('insights "{name}" report at least {count:d} session'))
def insights_report_session_count(insights_snapshots: InsightsSnapshots, name: str, count: int) -> None:
    """Verify the insight session count."""
    found = insights_snapshots.get(name).total_session_count
    assert found >= count, f"insights {name!r} report {found} sessions"


@then(
    parsers.parse(
        'insights "{after_name}" differ from "{before_name}" by exactly completed session "{session_name}"',
    ),
)
def insights_have_completed_session_delta(
    insight_session_context: InsightSessionContext,
    after_name: str,
    before_name: str,
    session_name: str,
) -> None:
    """Verify the insight delta contains one completed session."""
    assert_completed_session_delta(
        insight_session_context.snapshots.get(before_name),
        insight_session_context.snapshots.get(after_name),
        insight_session_context.client.sessions.snapshot(insight_session_context.sessions.get(session_name)),
    )
