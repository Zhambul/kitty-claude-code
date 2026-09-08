# Copyright (c) 2026 Zhambyl Yermagambet
"""Read and compare typed application-insight values."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import date, datetime

    from api.application.models.insights.application_insights_response import (
        ApplicationInsightsResponse,
        DailySessionCountResponse,
        HourlySessionCountResponse,
        InsightProjectSummaryResponse,
        ProjectInsightsResponse,
    )

FLOAT_COMPARISON_TOLERANCE = 1e-9


def project(insights: ApplicationInsightsResponse, working_directory: str) -> ProjectInsightsResponse | None:
    """Return the single project for a working directory.

    Returns:
        The project, if present.

    """
    found = [
        project_entry
        for project_entry in insights.projects
        if project_entry.working_directory == working_directory
    ]
    count = len(found)
    assert count <= 1, f"insights have {count} projects for {working_directory!r}"
    return found[0] if found else None


def project_summary_count(projects: tuple[InsightProjectSummaryResponse, ...], working_directory: str) -> int:
    """Return a project session count from one insight window.

    Returns:
        The project session count, or zero.

    """
    found = [
        project_entry.session_count
        for project_entry in projects
        if project_entry.working_directory == working_directory
    ]
    count = len(found)
    assert count <= 1, f"insight window has {count} projects for {working_directory!r}"
    return found[0] if found else 0


def daily_count(rows: tuple[DailySessionCountResponse, ...], day: date) -> int:
    """Return the session count for one local day.

    Returns:
        The day session count, or zero.

    """
    found = [row.session_count for row in rows if row.date == day]
    count = len(found)
    assert count <= 1, f"insights have {count} rows for {day}"
    return found[0] if found else 0


def hourly_count(rows: tuple[HourlySessionCountResponse, ...], started: datetime) -> int:
    """Return the session count for one local hour.

    Returns:
        The hour session count, or zero.

    """
    day_of_week = int(started.strftime("%w"))
    matching_day = [row for row in rows if row.day_of_week == day_of_week]
    found = [row.session_count for row in matching_day if row.hour == started.hour]
    count = len(found)
    assert count <= 1, f"insights have {count} rows for day {day_of_week}, hour {started.hour}"
    return found[0] if found else 0


def project_value(project_response: ProjectInsightsResponse | None, field: str) -> int | float:
    """Return a numeric project value or the absent-project default.

    Returns:
        The selected numeric value.

    """
    return 0 if project_response is None else getattr(project_response, field)


def assert_float_delta(before: float, after: float, expected_delta: float) -> None:
    """Verify one floating point value changed by an expected delta.

    Raises:
        AssertionError: If the value change differs from the expected delta.

    """
    if not math.isclose(
        after - before,
        expected_delta,
        rel_tol=FLOAT_COMPARISON_TOLERANCE,
        abs_tol=FLOAT_COMPARISON_TOLERANCE,
    ):
        actual_delta = after - before
        message = f"insight value changed by {actual_delta}, expected {expected_delta}"
        raise AssertionError(message)
