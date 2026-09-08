# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that start plan work and find plan controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit import planning_contexts, references as refs, selector_attention, selector_turns

if TYPE_CHECKING:
    from sdk.client import BaqylauClient


@when(parsers.parse('I start plan work "{turn_name}" in session "{session_name}" with prompt'))
def start_plan_work(
    plan_work_context: planning_contexts.PlanWorkContext,
    session_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Start plan work."""
    plan_work_context.turns.bind(
        turn_name,
        plan_work_context.driver.start(
            plan_work_context.session_specs.get(session_name),
            plan_work_context.sessions.get(session_name),
            docstring.strip(),
        ),
    )


@when(parsers.parse('I name the pending plan in turn "{turn_name}" containing \'{text}\' "{plan_name}"'))
def name_pending_plan(
    plan_observation_context: planning_contexts.PlanObservationContext,
    turn_name: str,
    text: str,
    plan_name: str,
) -> None:
    """Name a pending plan in one turn."""
    original = plan_observation_context.turns.get(turn_name)
    turn = selector_turns.turn(
        plan_observation_context.client.sessions.watch(original.session),
        original,
        plan_observation_context.wait_policy.turn,
    )
    plan_observation_context.turns.replace(turn_name, turn)
    plan_observation_context.plans.bind(
        plan_name,
        selector_attention.plan(
            plan_observation_context.client.sessions.watch(turn.session),
            turn_reference=turn,
            turn_name=turn_name,
            text_contains=text,
            timeout=plan_observation_context.wait_policy.turn,
        ),
    )


@when(parsers.parse('I read choices for plan "{plan_name}" as control "{control_name}"'))
def read_plan_choices(
    client: BaqylauClient,
    plans: refs.Plans,
    controls: refs.Controls,
    plan_name: str,
    control_name: str,
) -> None:
    """Read controls for one plan."""
    reference = plans.get(plan_name)
    controls.bind(
        control_name,
        client.sessions.read_plan_choices(reference.session, reference.attention_id),
    )
