# Copyright (c) 2026 Zhambyl Yermagambet
"""Test control effect plan resolution."""

from __future__ import annotations

import pytest

from domain import (
    event_work,
    ids as domain_ids,
    outcomes,
)
from harness.models import controls as control_models
from harness.models.raw_event_builders import (
    plan_resolution_phase,
)
from tests import (
    control_effect_entries as entries,
    control_effect_recording as recording,
    control_effect_values as control_values,
)


@pytest.mark.parametrize(
    ("decision", "feedback", "state"),
    [
        ("1", None, outcomes.PlanState.APPROVED),
        ("dismiss", None, outcomes.PlanState.REJECTED),
        ("feedback", "start with tests", outcomes.PlanState.CHANGES_REQUESTED),
    ],
)
def test_confirmed_plan_decision_becomes_one(
    decision: str,
    feedback: str | None,
    state: outcomes.PlanState,
) -> None:
    """Verify confirmed plan decision becomes one canonical resolution."""
    attention_id = domain_ids.AttentionId("plan-one")
    control_fixture = recording.control_effect_fixture()
    pending = entries.pending_plan_entry(attention_id)
    request = control_models.DecidePlan(
        control_fixture.session.session_id,
        control_values.TEST_REQUEST_ID,
        attention_id,
        decision,
        feedback,
    )

    control_fixture.recorder.plan_decided(control_fixture.session, request, pending)

    event = control_fixture.translated_event()
    assert event.actor_id == control_values.TEST_ACTOR_ID
    assert event.turn_id == control_values.TEST_TURN_ID
    assert event.payload == event_work.PlanResolved(
        attention_id=attention_id, state=state, feedback=feedback, edited=False,
    )


def test_plan_feedback_is_newer_revision() -> None:
    """Verify plan feedback is a newer revision than a generic rejection."""
    attention_id = domain_ids.AttentionId("plan-one")
    generic = event_work.PlanResolved(
        attention_id=attention_id, state=outcomes.PlanState.REJECTED, feedback=None, edited=False,
    )
    feedback = event_work.PlanResolved(
        attention_id=attention_id,
        state=outcomes.PlanState.CHANGES_REQUESTED,
        feedback="start with tests",
        edited=False,
    )

    assert plan_resolution_phase(generic) != plan_resolution_phase(feedback)
