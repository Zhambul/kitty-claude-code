# Copyright (c) 2026 Zhambyl Yermagambet
"""Named skill acquisition and lifecycle checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit import selector_operations
from tests.e2e.testkit.references import (
    SkillRef,
    Skills,
    WorkerKind,
)

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot, SkillState
    from tests.e2e.testkit.action_contexts import (
        SkillLaunchContext,
        SkillObservationContext,
    )
    from tests.e2e.testkit.policy import WaitPolicy


def _skill(snapshot: SessionSnapshot, reference: SkillRef) -> SkillState:
    found = [skill_state for skill_state in snapshot.skills() if skill_state.skill_id == reference.skill_id]
    if len(found) != 1:
        message = f"skill {reference.skill_id!r} has {len(found)} matches"
        raise AssertionError(message)
    return found[0]


@when(
    parsers.parse(
        'I launch session "{session_name}" and assign work "{work_name}" '
        'to the {worker_type} using test skill "{skill_name}"',
    ),
)
def launch_skill_work(
    skill_launch_context: SkillLaunchContext,
    session_name: str,
    work_name: str,
    worker_type: str,
    skill_name: str,
) -> None:
    """Launch skill work.

    Raises:
        AssertionError: If the worker type is unknown.

    """
    try:
        worker_kind = WorkerKind(worker_type)
    except ValueError as error:
        message = f"unknown worker type {worker_type!r}"
        raise AssertionError(message) from error
    started = skill_launch_context.driver.launch(
        skill_launch_context.session_specs.get(session_name),
        work_name=work_name,
        worker_kind=worker_kind,
        skill_name=skill_name,
    )
    skill_launch_context.sessions.bind(session_name, started.session)
    skill_launch_context.works.bind(work_name, started.work)
    skill_launch_context.turns.bind(work_name, started.work.turn)


@when(
    parsers.parse(
        'I name the skill in turn "{turn_name}" with exact name \'{exact_name}\' "{skill_name}"',
    ),
)
@when(
    parsers.parse(
        'I name the skill in work "{turn_name}" with exact name \'{exact_name}\' "{skill_name}"',
    ),
)
@when(
    parsers.parse(
        'I name test skill "{exact_name}" in work "{turn_name}" "{skill_name}"',
    ),
)
def name_skill(
    skill_observation_context: SkillObservationContext,
    turn_name: str,
    exact_name: str,
    skill_name: str,
) -> None:
    """Process name skill."""
    turn = skill_observation_context.turns.get(turn_name)
    found = selector_operations.skill(
        skill_observation_context.client.sessions.watch(turn.session),
        turn_reference=turn,
        exact_name=exact_name,
        timeout=skill_observation_context.wait_policy.feed,
    )
    skill_observation_context.skills.bind(skill_name, found)


@then(parsers.parse('skill "{name}" has state {state}'))
def skill_has_state(
    client: BaqylauClient,
    skills: Skills,
    wait_policy: WaitPolicy,
    name: str,
    state: str,
) -> None:
    """Process skill has state."""
    reference = skills.get(name)
    client.sessions.watch(reference.session).wait(
        f"skill {name!r} to have state {state!r}",
        lambda snapshot: True if _skill(snapshot, reference).state == state else None,
        timeout=wait_policy.feed,
    )


@then(parsers.parse('skill "{name}" has no arguments'))
def skill_has_no_arguments(
    client: BaqylauClient,
    skills: Skills,
    name: str,
) -> None:
    """Process skill has no arguments."""
    reference = skills.get(name)
    assert not _skill(client.sessions.snapshot(reference.session), reference).arguments


@then(parsers.parse("skill \"{name}\" has arguments '{arguments}'"))
def skill_has_arguments(
    client: BaqylauClient,
    skills: Skills,
    name: str,
    arguments: str,
) -> None:
    """Process skill has arguments."""
    reference = skills.get(name)
    assert _skill(client.sessions.snapshot(reference.session), reference).arguments == arguments


@then(parsers.parse("skill \"{name}\" has result containing '{text}'"))
def skill_has_result(
    client: BaqylauClient,
    skills: Skills,
    name: str,
    text: str,
) -> None:
    """Process skill has result."""
    reference = skills.get(name)
    assert text in _skill(client.sessions.snapshot(reference.session), reference).result
