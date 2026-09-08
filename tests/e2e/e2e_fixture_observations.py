# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture observations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies

if TYPE_CHECKING:
    from sdk.client import SessionRef


@fixture_dependencies.application.pytest.fixture
def plan_work_driver(
    client: fixture_dependencies.harness.BaqylauClient,
) -> fixture_dependencies.contexts.PlanWorkDriver:
    """Build the plan-work driver.

    Returns:
        The plan-work driver for the supplied client.

    """
    return fixture_dependencies.contexts.PlanWorkDriver(client)


@fixture_dependencies.application.pytest.fixture
def shell_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    shells: fixture_dependencies.drivers.refs.Shells,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.action_contexts.ShellObservationContext:
    """Return services for shell observations.

    Returns:
        Services for shell observations.

    """
    return fixture_dependencies.drivers.action_contexts.ShellObservationContext(client, turns, shells, wait_policy)


@fixture_dependencies.application.pytest.fixture
def assignment_naming_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    assignments: fixture_dependencies.drivers.refs.Assignments,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext[
    fixture_dependencies.drivers.refs.TurnRef, fixture_dependencies.drivers.refs.AssignmentRef,
]:
    """Return services that name assignments from turns.

    Returns:
        Services that name assignments from turns.

    """
    return fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext(
        client, turns, assignments, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def assigned_actor_naming_context(
    client: fixture_dependencies.harness.BaqylauClient,
    assignments: fixture_dependencies.drivers.refs.Assignments,
    actors: fixture_dependencies.drivers.refs.Actors,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext[
    fixture_dependencies.drivers.refs.AssignmentRef, fixture_dependencies.drivers.refs.ActorRef,
]:
    """Return services that name actors from assignments.

    Returns:
        Services that name actors from assignments.

    """
    return fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext(
        client, assignments, actors, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def subagent_naming_context(
    client: fixture_dependencies.harness.BaqylauClient,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    actors: fixture_dependencies.drivers.refs.Actors,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext[
    SessionRef, fixture_dependencies.drivers.refs.ActorRef,
]:
    """Return services that name subagents from sessions.

    Returns:
        Services that name subagents from sessions.

    """
    return fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext(
        client, sessions, actors, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def actor_command_naming_context(
    client: fixture_dependencies.harness.BaqylauClient,
    actors: fixture_dependencies.drivers.refs.Actors,
    shells: fixture_dependencies.drivers.refs.Shells,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext[
    fixture_dependencies.drivers.refs.ActorRef, fixture_dependencies.drivers.refs.ShellRef,
]:
    """Return services that name commands from actors.

    Returns:
        Services that name commands from actors.

    """
    return fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext(client, actors, shells, wait_policy)


@fixture_dependencies.application.pytest.fixture
def actor_message_naming_context(
    client: fixture_dependencies.harness.BaqylauClient,
    works: fixture_dependencies.drivers.refs.Works,
    actor_messages: fixture_dependencies.drivers.refs.ActorMessages,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext[
    fixture_dependencies.drivers.refs.WorkRef, fixture_dependencies.drivers.refs.ActorMessageRef,
]:
    """Return services that name messages from work.

    Returns:
        Services that name messages from work.

    """
    return fixture_dependencies.contexts.reference_contexts.ReferenceBindingContext(
        client, works, actor_messages, wait_policy,
    )
