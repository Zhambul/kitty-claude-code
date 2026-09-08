# Copyright (c) 2026 Zhambyl Yermagambet
"""Aggregate session starts by local date and hour."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime

from app.services import insight_models as models


def daily_sessions(
    rows: tuple[models.SessionInsight, ...],
) -> tuple[models.DailySessionCount, ...]:
    """Count session starts for each local calendar date.

    Returns:
        Result items.

    """
    counts = Counter(_local_datetime(row.started_at).date() for row in rows)
    return tuple(map(_daily_count, sorted(counts.items())))


def hourly_sessions(
    rows: tuple[models.SessionInsight, ...],
) -> tuple[models.HourlySessionCount, ...]:
    """Count session starts for each local weekday and hour.

    Returns:
        Result items.

    """
    counts = Counter(_hour_key(row) for row in rows)
    result = []
    for (day, hour), session_count in sorted(counts.items()):
        result.append(models.HourlySessionCount(day, hour, session_count))
    return tuple(result)


def _local_datetime(timestamp: float) -> datetime:
    return datetime.fromtimestamp(timestamp, tz=UTC).astimezone()


def _hour_key(row: models.SessionInsight) -> tuple[int, int]:
    started = _local_datetime(row.started_at)
    return int(started.strftime("%w")), started.hour


def _daily_count(count: tuple[date, int]) -> models.DailySessionCount:
    return models.DailySessionCount(*count)
