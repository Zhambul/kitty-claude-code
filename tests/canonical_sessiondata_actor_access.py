# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata actor access."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests import canonical_sessiondata_components as sessiondata_components, canonical_sessiondata_folding as folding

if TYPE_CHECKING:
    from tests.canonical_sessiondata_components import domain as session_domain


def lead_actor(
    state: sessiondata_components.engine.contract.AggregateState,
) -> session_domain.actor_state.ActorFacts:
    """Return lead facts for assertions that span several fields.

    Returns:
        Lead facts for assertions that span several fields.

    """
    return folding.lead_from(state)


def lead_model(
    state: sessiondata_components.engine.contract.AggregateState,
) -> session_domain.references.ModelReference | None:
    """Return the selected model for the lead actor.

    Returns:
        The selected model for the lead actor.

    """
    return folding.lead_from(state).model


def lead_effort(state: sessiondata_components.engine.contract.AggregateState) -> str | None:
    """Return the selected effort for the lead actor.

    Returns:
        The selected effort for the lead actor.

    """
    return folding.lead_from(state).effort


def lead_status(
    state: sessiondata_components.engine.contract.AggregateState,
) -> session_domain.actor_state.ActorStatus | None:
    """Return the visible status for the lead actor.

    Returns:
        The visible status for the lead actor.

    """
    return folding.lead_from(state).status


def lead_background(
    state: sessiondata_components.engine.contract.AggregateState,
) -> session_domain.actor_state.ActorBackground:
    """Return the background-work state for the lead actor.

    Returns:
        The background-work state for the lead actor.

    """
    return folding.lead_from(state).background


def lead_context(
    state: sessiondata_components.engine.contract.AggregateState,
) -> session_domain.actor_state.ActorContext:
    """Return the context-window state for the lead actor.

    Returns:
        The context-window state for the lead actor.

    """
    return folding.lead_from(state).context


def lead_statistics(
    state: sessiondata_components.engine.contract.AggregateState,
) -> session_domain.actor_state.ActorStatistics:
    """Return the work statistics for the lead actor.

    Returns:
        The work statistics for the lead actor.

    """
    return folding.lead_from(state).statistics
