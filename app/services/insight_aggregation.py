# Copyright (c) 2026 Zhambyl Yermagambet
"""Aggregate collected session insight rows."""

from __future__ import annotations

from collections import Counter
from functools import partial
from itertools import groupby
from pathlib import Path

from app.services import insight_models as models, insight_timeline as timeline

DAYS_PER_WEEK = 7
DAYS_PER_MONTH_WINDOW = 30
SECONDS_PER_DAY = 86_400


class InsightAggregator:
    """Build application windows and project aggregates."""

    def __init__(self, top_project_count: int) -> None:
        """Create an aggregator with a project summary limit."""
        self.top_project_count = top_project_count

    def aggregate(
        self,
        rows: tuple[models.SessionInsight, ...],
        generated_at: float,
    ) -> models.ApplicationInsights:
        """Build all application insights from collected session rows.

        Returns:
            The application insights.

        """
        return models.ApplicationInsights(
            generated_at=generated_at,
            total_session_count=len(rows),
            daily_sessions=timeline.daily_sessions(rows),
            hourly_sessions=timeline.hourly_sessions(rows),
            last_seven_days=self._window(
                rows,
                generated_at - DAYS_PER_WEEK * SECONDS_PER_DAY,
            ),
            last_thirty_days=self._window(
                rows,
                generated_at - DAYS_PER_MONTH_WINDOW * SECONDS_PER_DAY,
            ),
            all_time=self._window(rows, None),
            projects=_projects(rows),
        )

    def _window(
        self,
        rows: tuple[models.SessionInsight, ...],
        started_after: float | None,
    ) -> models.InsightWindow:
        selected_rows = tuple(
            filter(
                partial(_in_window, started_after=started_after),
                rows,
            ),
        )
        return models.InsightWindow(
            session_count=len(selected_rows),
            active_session_count=sum(row.active for row in selected_rows),
            finished_session_count=sum(row.finished for row in selected_rows),
            token_count=sum(row.token_count for row in selected_rows),
            cost_in_usd=sum(row.cost_in_usd for row in selected_rows),
            error_count=sum(row.error_count for row in selected_rows),
            projects=self._top_projects(selected_rows),
        )

    def _top_projects(
        self,
        rows: tuple[models.SessionInsight, ...],
    ) -> tuple[models.InsightProjectSummary, ...]:
        project_counts = Counter(row.working_directory for row in rows if row.working_directory)
        ranked_projects = sorted(
            project_counts.items(),
            key=lambda project_count: (-project_count[1], project_count[0]),
        )[: self.top_project_count]
        return tuple(
            models.InsightProjectSummary(
                working_directory=directory,
                name=_project_name(directory),
                session_count=session_count,
            )
            for directory, session_count in ranked_projects
        )


def _project_insights(
    directory: str,
    rows: tuple[models.SessionInsight, ...],
) -> models.ProjectInsights:
    return models.ProjectInsights(
        working_directory=directory,
        name=_project_name(directory),
        session_count=len(rows),
        token_count=sum(row.token_count for row in rows),
        cost_in_usd=sum(row.cost_in_usd for row in rows),
        error_count=sum(row.error_count for row in rows),
        last_session_at=max(row.started_at for row in rows),
        daily_sessions=timeline.daily_sessions(rows),
    )


def _project_name(directory: str) -> str:
    return Path(directory).name or directory


def _in_window(
    row: models.SessionInsight,
    *,
    started_after: float | None,
) -> bool:
    return started_after is None or row.started_at >= started_after


def _projects(
    rows: tuple[models.SessionInsight, ...],
) -> tuple[models.ProjectInsights, ...]:
    project_rows = (row for row in rows if row.working_directory)
    ordered_rows = sorted(
        project_rows,
        key=lambda session_insight: session_insight.working_directory,
    )
    projects = tuple(
        _project_insights(directory, tuple(group_rows))
        for directory, group_rows in groupby(
            ordered_rows,
            key=lambda session_insight: session_insight.working_directory,
        )
    )
    return tuple(
        sorted(
            projects,
            key=lambda project: (-project.session_count, project.name),
        ),
    )
