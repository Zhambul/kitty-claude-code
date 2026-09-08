# Copyright (c) 2026 Zhambyl Yermagambet
"""Collect cross-session application insight rows."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from app.services import insight_models as models
from app.services.insight_aggregation import InsightAggregator

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from app.services.insight_resources import ApplicationInsightResources
    from domain.ids import SessionId
    from domain.session_state import SessionData
    from domain.usage import TokenUsage


class ApplicationInsightsService:
    """Collect session insight rows and build application aggregates."""

    def __init__(
        self,
        application_insight_resources: ApplicationInsightResources,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """Create a service with canonical and operational readers."""
        self.read_model = application_insight_resources.session_data_repository
        self.terminal = application_insight_resources.terminal_session_reader
        self.audit = application_insight_resources.audit_read_repository
        self.repositories = application_insight_resources.repository_queries
        self.aggregator = InsightAggregator(application_insight_resources.top_project_count)
        self.clock = clock

    def snapshot(self) -> models.ApplicationInsights:
        """Return a current cross-session insight snapshot.

        Returns:
            A current cross-session insight snapshot.

        """
        generated_at = self.clock()
        error_counts = self.audit.error_counts()
        rows = self._session_rows(error_counts)
        return self.aggregator.aggregate(rows, generated_at)

    def _session_rows(
        self,
        error_counts: Mapping[SessionId, int],
    ) -> tuple[models.SessionInsight, ...]:
        rows: list[models.SessionInsight] = []
        for session_data in self.read_model.visible():
            session_insight = self._session_insight(session_data, error_counts)
            if session_insight is not None:
                rows.append(session_insight)
        return tuple(rows)

    def _session_insight(
        self,
        session_data: SessionData,
        error_counts: Mapping[SessionId, int],
    ) -> models.SessionInsight | None:
        session = session_data.session
        if session.started_at is None:
            return None
        return models.SessionInsight(
            session_id=session.session_id,
            working_directory=self.repositories.project_directory(
                session.working_directory,
            ),
            started_at=session.started_at,
            finished=session.state == "finished",
            active=self.terminal.state(session.session_id).window_id is not None,
            token_count=sum(_token_count(actor.usage.tokens) for actor in session_data.actors),
            cost_in_usd=sum(float(actor.usage.cost_in_usd or 0) for actor in session_data.actors),
            error_count=error_counts.get(session.session_id, 0),
        )


def _token_count(token_usage: TokenUsage) -> int:
    return (
        token_usage.input_tokens
        + token_usage.output_tokens
        + token_usage.cache_read_tokens
        + token_usage.cache_write_tokens
        + token_usage.one_hour_cache_write_tokens
    )
