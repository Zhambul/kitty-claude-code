# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check plan state and plan controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from api.controls.models.control_outcome_response import PlanChoicesResultResponse
from tests.e2e.testkit import plan_choices, planning_contexts, references as refs
from tests.e2e.testkit.planning import PlanAnswerExpectation, plan_state, wait_for_plan_answer

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.policy import WaitPolicy


@then(parsers.parse("plan \"{name}\" contains '{text}'"))
def plan_contains(client: BaqylauClient, plans: refs.Plans, name: str, text: str) -> None:
    """Check text in one plan."""
    reference = plans.get(name)
    assert text in plan_state(client.sessions.snapshot(reference.session), reference).text


@then(parsers.parse("control \"{name}\" offers a plan option containing '{label}'"))
def control_offers_plan_option(controls: refs.Controls, name: str, label: str) -> None:
    """Check that a plan control offers one option."""
    outcome = controls.get(name).outcome
    assert isinstance(outcome, PlanChoicesResultResponse)
    assert any(plan_choices.label_contains(label, choice.label) for choice in outcome.choices)


@then(parsers.parse('control "{name}" offers an approval plan option'))
def control_offers_approval_plan_option(controls: refs.Controls, name: str) -> None:
    """Check that a plan control offers approval."""
    outcome = controls.get(name).outcome
    assert isinstance(outcome, PlanChoicesResultResponse)
    assert any(not choice.feedback for choice in outcome.choices)


@then(parsers.parse('plan "{name}" has state {state}'))
def plan_has_state(
    client: BaqylauClient,
    plans: refs.Plans,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Wait for one plan state."""
    reference = plans.get(name)
    client.sessions.watch(reference.session).wait(
        f"plan {name!r} to have state {state!r}",
        lambda snapshot: True if plan_state(snapshot, reference).state == state else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse("plan \"{name}\" has feedback '{feedback}'"))
def plan_has_feedback(
    client: BaqylauClient,
    plans: refs.Plans,
    wait_policy: WaitPolicy,
    name: str,
    feedback: str,
) -> None:
    """Wait for one plan feedback value."""
    reference = plans.get(name)
    client.sessions.watch(reference.session).wait(
        f"plan {name!r} to have feedback {feedback!r}",
        lambda snapshot: True if plan_state(snapshot, reference).feedback == feedback else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('plan "{plan_name}" is followed by final answer \'{text}\' after control "{control_name}"'))
def plan_is_followed_by_final_answer(
    plan_interaction_context: planning_contexts.PlanInteractionContext,
    plan_name: str,
    text: str,
    control_name: str,
) -> None:
    """Wait for the final answer after one plan control."""
    reference = plan_interaction_context.plans.get(plan_name)
    control = plan_interaction_context.controls.get(control_name)
    wait_for_plan_answer(
        plan_interaction_context.client,
        reference,
        PlanAnswerExpectation(
            control.cursor_before,
            text,
            plan_name,
            plan_interaction_context.wait_policy.turn,
        ),
    )
