# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata status assignments."""

from __future__ import annotations

from tests import (
    canonical_sessiondata_actor_access as actor_access,
    canonical_sessiondata_fixtures as session_fixtures,
    canonical_sessiondata_folding as folding,
    canonical_sessiondata_values as session_values,
)
from tests.canonical_sessiondata_components import domain as session_domain


def test_lead_that_ends_its_turn_over_subagent() -> None:
    """Verify a lead that ends its turn over subagent work is awaiting it."""
    assignment_id = session_values.FIRST_ASSIGNMENT_ID

    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_actor.ActorAssignmentStarted(
            assignment_id, session_domain.content.TextContent(session_values.ASSIGNMENT_PROMPT),
        ),
        session_fixtures.succeeded_turn(),
    )

    lead = actor_access.lead_actor(state)
    assert lead is not None
    assert lead.status == "awaiting_background"
    assert lead.running_assignment_ids_internal == (assignment_id,)


def test_codex_child_assignment_start_is_owned() -> None:
    """Verify a codex child assignment start is owned by its lead."""
    assignment_id = session_values.FIRST_ASSIGNMENT_ID

    state = folding.fold(
        *session_fixtures.alive(),
        folding.committed(
            session_domain.event_actor.ActorStarted(
                session_values.CHILD_ACTOR_NAME,
                session_domain.messaging.ActorRole.CHILD,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=10,
        ),
        folding.committed(
            session_domain.event_actor.ActorAssignmentStarted(
                assignment_id, session_domain.content.TextContent(session_values.ASSIGNMENT_PROMPT),
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=session_values.ASSIGNMENT_RESULT_CURSOR,
        ),
        session_fixtures.succeeded_turn(),
    )

    lead = actor_access.lead_actor(state)
    assert lead is not None
    assert lead.status == "awaiting_background"
    assert lead.running_assignment_ids_internal == (assignment_id,)


def test_child_assignment_result_releases_lead() -> None:
    """Verify a child assignment result releases a lead whose turn ended."""
    assignment_id = session_values.FIRST_ASSIGNMENT_ID

    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_actor.ActorAssignmentStarted(
            assignment_id, session_domain.content.TextContent(session_values.ASSIGNMENT_PROMPT),
        ),
        session_fixtures.succeeded_turn(),
        folding.committed(
            session_domain.event_actor.ActorStarted(
                session_values.CHILD_ACTOR_NAME,
                session_domain.messaging.ActorRole.CHILD,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=10,
        ),
        folding.committed(
            session_domain.event_actor.ActorAssignmentFinished(
                assignment_id,
                session_domain.outcomes.Outcome.SUCCEEDED,
                session_domain.content.TextContent("verified"),
                None,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=session_values.ASSIGNMENT_RESULT_CURSOR,
        ),
    )

    lead = actor_access.lead_actor(state)
    child = folding.actor_from(state, session_values.CHILD)
    assert lead is not None
    assert child is not None
    assert lead.status == session_values.AWAITING_RESPONSE_STATE
    assert lead.running_assignment_ids_internal == ()
    assert child.state == session_values.FINISHED_STATE


def test_late_child_start_result_releases_lead() -> None:
    """Verify a child start after the lead turn does not reopen the lead."""
    assignment_id = session_values.FIRST_ASSIGNMENT_ID

    state = folding.fold(
        *session_fixtures.alive(),
        session_fixtures.succeeded_turn(),
        folding.committed(
            session_domain.event_actor.ActorStarted(
                session_values.CHILD_ACTOR_NAME,
                session_domain.messaging.ActorRole.CHILD,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=session_values.ASSIGNMENT_START_CURSOR,
        ),
        folding.committed(
            session_domain.event_actor.ActorAssignmentStarted(
                assignment_id,
                session_domain.content.TextContent(session_values.ASSIGNMENT_PROMPT),
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=session_values.ASSIGNMENT_RESULT_CURSOR,
        ),
        folding.committed(
            session_domain.event_actor.ActorAssignmentFinished(
                assignment_id,
                session_domain.outcomes.Outcome.SUCCEEDED,
                session_domain.content.TextContent("verified"),
                None,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=session_values.ASSIGNMENT_RESULT_CURSOR,
        ),
    )

    lead = actor_access.lead_actor(state)
    assert lead is not None
    assert lead.status == session_values.AWAITING_RESPONSE_STATE
    assert lead.running_assignment_ids_internal == ()


def test_child_assignment_result_keeps_active() -> None:
    """Verify a child assignment result keeps an active lead working."""
    assignment_id = session_values.FIRST_ASSIGNMENT_ID

    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_actor.ActorAssignmentStarted(
            assignment_id, session_domain.content.TextContent(session_values.ASSIGNMENT_PROMPT),
        ),
        folding.committed(
            session_domain.event_actor.ActorStarted(
                session_values.CHILD_ACTOR_NAME,
                session_domain.messaging.ActorRole.CHILD,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=10,
        ),
        folding.committed(
            session_domain.event_actor.ActorAssignmentFinished(
                assignment_id,
                session_domain.outcomes.Outcome.SUCCEEDED,
                session_domain.content.TextContent("verified"),
                None,
            ),
            actor_id=session_values.CHILD,
            parent_actor_id=session_values.LEAD,
            cursor=session_values.ASSIGNMENT_RESULT_CURSOR,
        ),
    )

    lead = actor_access.lead_actor(state)
    assert lead is not None
    assert lead.status == session_values.WORKING_STATE
    assert lead.running_assignment_ids_internal == ()


def test_failed_assignment_launch_does_not_finish() -> None:
    """Verify a failed assignment launch does not finish the lead."""
    assignment_id = session_values.FIRST_ASSIGNMENT_ID

    state = folding.fold(
        *session_fixtures.alive(),
        session_domain.event_actor.ActorAssignmentStarted(
            assignment_id, session_domain.content.TextContent(session_values.ASSIGNMENT_PROMPT),
        ),
        session_domain.event_actor.ActorAssignmentFinished(
            assignment_id, session_domain.outcomes.Outcome.FAILED, None, "not found",
        ),
    )

    lead = actor_access.lead_actor(state)
    assert lead is not None
    assert lead.state == session_values.RUNNING_STATE
    assert lead.status == session_values.WORKING_STATE
    assert lead.running_assignment_ids_internal == ()
