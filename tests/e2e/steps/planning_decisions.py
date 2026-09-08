# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that make decisions for named plans."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from api.controls.models.control_outcome_response import PlanChoicesResultResponse
from tests.e2e.testkit import plan_choices, planning_contexts, references as refs

if TYPE_CHECKING:
    from sdk.client import BaqylauClient


@when(
    parsers.parse(
        "I choose plan option containing '{label}' from control \"{choices_name}\" "
        'for plan "{plan_name}" as control "{control_name}"',
    ),
)
def choose_plan_option(
    plan_interaction_context: planning_contexts.PlanInteractionContext,
    label: str,
    choices_name: str,
    plan_name: str,
    control_name: str,
) -> None:
    """Choose one named plan option.

    Raises:
        AssertionError: If the label does not identify one choice.
        TypeError: If the control does not contain plan choices.

    """
    outcome = plan_interaction_context.controls.get(choices_name).outcome
    if not isinstance(outcome, PlanChoicesResultResponse):
        message = f"control {choices_name!r} has no plan choices"
        raise TypeError(message)
    matches = plan_choices.matches(outcome.choices, label)
    if len(matches) != 1:
        message = f"plan choice containing {label!r} has {len(matches)} matches: {outcome.choices}"
        raise AssertionError(message)
    reference = plan_interaction_context.plans.get(plan_name)
    receipt = plan_interaction_context.controls.bind(
        control_name,
        plan_interaction_context.client.sessions.decide_plan(
            reference.session,
            attention_id=reference.attention_id,
            decision=matches[0].digit,
        ),
    )
    plan_interaction_context.turns.replace(
        reference.turn_name,
        plan_interaction_context.turns.get(reference.turn_name).resumed_after(receipt.cursor_before),
    )


@when(parsers.parse('I approve plan "{plan_name}" from control "{choices_name}" as control "{control_name}"'))
def approve_plan(
    plan_interaction_context: planning_contexts.PlanInteractionContext,
    plan_name: str,
    choices_name: str,
    control_name: str,
) -> None:
    """Approve one plan.

    Raises:
        AssertionError: If the control has no approval choice.
        TypeError: If the control does not contain plan choices.

    """
    outcome = plan_interaction_context.controls.get(choices_name).outcome
    if not isinstance(outcome, PlanChoicesResultResponse):
        message = f"control {choices_name!r} has no plan choices"
        raise TypeError(message)
    choices = [choice for choice in outcome.choices if not choice.feedback]
    if not choices:
        message = f"control {choices_name!r} has no approval choice"
        raise AssertionError(message)
    reference = plan_interaction_context.plans.get(plan_name)
    receipt = plan_interaction_context.controls.bind(
        control_name,
        plan_interaction_context.client.sessions.decide_plan(
            reference.session,
            attention_id=reference.attention_id,
            decision=choices[0].digit,
        ),
    )
    plan_interaction_context.turns.replace(
        reference.turn_name,
        plan_interaction_context.turns.get(reference.turn_name).resumed_after(receipt.cursor_before),
    )


@when(parsers.parse('I dismiss plan "{plan_name}" as control "{control_name}"'))
def dismiss_plan(
    client: BaqylauClient,
    plans: refs.Plans,
    controls: refs.Controls,
    plan_name: str,
    control_name: str,
) -> None:
    """Dismiss one plan."""
    reference = plans.get(plan_name)
    controls.bind(
        control_name,
        client.sessions.decide_plan(reference.session, attention_id=reference.attention_id, decision="dismiss"),
    )


@when(parsers.parse('I request plan changes \'{feedback}\' for plan "{plan_name}" as control "{control_name}"'))
def request_plan_changes(
    plan_interaction_context: planning_contexts.PlanInteractionContext,
    feedback: str,
    plan_name: str,
    control_name: str,
) -> None:
    """Request changes for one plan."""
    reference = plan_interaction_context.plans.get(plan_name)
    plan_interaction_context.controls.bind(
        control_name,
        plan_interaction_context.client.sessions.decide_plan(
            reference.session,
            attention_id=reference.attention_id,
            decision="feedback",
            feedback=feedback,
        ),
    )
