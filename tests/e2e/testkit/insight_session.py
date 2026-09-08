# Copyright (c) 2026 Zhambyl Yermagambet
"""Derive completed-session facts for insight assertions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.sessiondata.models.actor import ActorResponse
    from sdk.state import SessionSnapshot


@dataclass(frozen=True)
class CompletedSessionDelta:
    """Describe the insight contribution of one completed session."""

    started: datetime
    working_directory: str
    token_count: int
    cost_in_usd: float
    started_at: float


def completed_session_delta(session: SessionSnapshot) -> CompletedSessionDelta:
    """Return the insight contribution of a completed session.

    Returns:
        The completed-session contribution.

    Raises:
        AssertionError: If the session has no start time or is unfinished.

    """
    summary = session.session_data.session
    if summary.started_at is None:
        message = f"session {summary.session_id!r} has no start time"
        raise AssertionError(message)
    if summary.state != "finished":
        message = f"session {summary.session_id!r} has state {summary.state!r}"
        raise AssertionError(message)
    token_count = sum(
        actor.usage.tokens.input_tokens
        + actor.usage.tokens.output_tokens
        + actor.usage.tokens.cache_read_tokens
        + actor.usage.tokens.cache_write_tokens
        + actor.usage.tokens.one_hour_cache_write_tokens
        for actor in session.session_data.actors
    )
    return CompletedSessionDelta(
        datetime.fromtimestamp(summary.started_at, tz=UTC).astimezone(),
        summary.working_directory,
        token_count,
        session_cost_in_usd(session),
        summary.started_at,
    )


def session_cost_in_usd(session: SessionSnapshot) -> float:
    """Return total actor cost for a session.

    Returns:
        The total session cost.

    """
    return sum(actor_cost_in_usd(actor) for actor in session.session_data.actors)


def actor_cost_in_usd(actor: ActorResponse) -> float:
    """Return one actor cost as a float.

    Returns:
        The actor cost.

    """
    return float(actor.usage.cost_in_usd or 0)
