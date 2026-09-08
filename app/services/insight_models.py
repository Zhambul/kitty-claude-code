# Copyright (c) 2026 Zhambyl Yermagambet
"""Declare application insight aggregates."""

from dataclasses import dataclass
from datetime import date

from domain.ids import SessionId


@dataclass(frozen=True)
class DailySessionCount:
    """Count sessions for one local calendar date."""

    date: date
    session_count: int


@dataclass(frozen=True)
class HourlySessionCount:
    """Count sessions for one weekday and local hour."""

    day_of_week: int
    hour: int
    session_count: int


@dataclass(frozen=True)
class InsightProjectSummary:
    """Summarize project activity in one insight window."""

    working_directory: str
    name: str
    session_count: int


@dataclass(frozen=True)
class InsightWindow:
    """Aggregate sessions after one optional start time."""

    session_count: int
    active_session_count: int
    finished_session_count: int
    token_count: int
    cost_in_usd: float
    error_count: int
    projects: tuple[InsightProjectSummary, ...]


@dataclass(frozen=True)
class ProjectInsights:
    """Aggregate all sessions for one project."""

    working_directory: str
    name: str
    session_count: int
    token_count: int
    cost_in_usd: float
    error_count: int
    last_session_at: float
    daily_sessions: tuple[DailySessionCount, ...]


@dataclass(frozen=True)
class ApplicationInsights:
    """Hold all cross-session application insights."""

    generated_at: float
    total_session_count: int
    daily_sessions: tuple[DailySessionCount, ...]
    hourly_sessions: tuple[HourlySessionCount, ...]
    last_seven_days: InsightWindow
    last_thirty_days: InsightWindow
    all_time: InsightWindow
    projects: tuple[ProjectInsights, ...]


@dataclass(frozen=True)
class SessionInsight:
    """Hold the insight fields collected for one session."""

    session_id: SessionId
    working_directory: str
    started_at: float
    finished: bool
    active: bool
    token_count: int
    cost_in_usd: float
    error_count: int
