# Copyright (c) 2026 Zhambyl Yermagambet
"""Check that a plan test waits for the native turn to end."""

from unittest.mock import Mock

from api.sessiondata.models.entry import EntryResponse, MessageBodyResponse
from sdk.state import SessionSnapshot
from sdk.state_models import PlanState
from tests.e2e.testkit.planning import PlanAnswerExpectation, _has_exact_plan_answer
from tests.e2e.testkit.references import PlanRef

PLAN_ID = "plan"


def test_final_plan_text_requires_turn_end() -> None:
    """Do not send a new mode command while the prior turn is active."""
    reference = Mock(spec=PlanRef, attention_id=PLAN_ID)
    snapshot = Mock(spec=SessionSnapshot)
    snapshot.plans.return_value = [PlanState(PLAN_ID, "lead", "turn", PLAN_ID, 1)]
    body = Mock(spec=MessageBodyResponse, role="assistant", phase="end_turn")
    body.content = Mock(text="DONE")
    snapshot.entries = [
        Mock(spec=EntryResponse, cursor=3, actor_id="lead", turn_id="turn", body=body),
    ]
    expectation = PlanAnswerExpectation(2, "DONE", PLAN_ID, 1)
    snapshot.turn_state.return_value = None
    assert _has_exact_plan_answer(snapshot, reference, expectation) is None
    snapshot.turn_state.return_value = "succeeded"
    assert _has_exact_plan_answer(snapshot, reference, expectation) is True
