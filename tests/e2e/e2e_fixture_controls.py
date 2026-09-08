# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture controls."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def workspace_file_context(
    client: fixture_dependencies.harness.BaqylauClient,
    workspace: str,
    turns: fixture_dependencies.drivers.refs.Turns,
    file_operations: fixture_dependencies.drivers.refs.FileOperations,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.action_contexts.WorkspaceFileContext:
    """Return services for workspace file observations.

    Returns:
        Services for workspace file observations.

    """
    return fixture_dependencies.drivers.action_contexts.WorkspaceFileContext(
        client, workspace, turns, file_operations, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def skill_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    skills: fixture_dependencies.drivers.refs.Skills,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.action_contexts.SkillObservationContext:
    """Return services for skill observations.

    Returns:
        Services for skill observations.

    """
    return fixture_dependencies.drivers.action_contexts.SkillObservationContext(client, turns, skills, wait_policy)


@fixture_dependencies.application.pytest.fixture
def search_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    searches: fixture_dependencies.drivers.refs.Searches,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.action_contexts.TurnObservationContext[fixture_dependencies.drivers.refs.SearchRef]:
    """Return services for named search observations.

    Returns:
        Services for named search observations.

    """
    return fixture_dependencies.drivers.action_contexts.TurnObservationContext(client, turns, searches, wait_policy)


@fixture_dependencies.application.pytest.fixture
def web_fetch_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    web_fetches: fixture_dependencies.drivers.refs.WebFetches,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.action_contexts.TurnObservationContext[fixture_dependencies.drivers.refs.WebFetchRef]:
    """Return services for named web fetch observations.

    Returns:
        Services for named web fetch observations.

    """
    return fixture_dependencies.drivers.action_contexts.TurnObservationContext(client, turns, web_fetches, wait_policy)


@fixture_dependencies.application.pytest.fixture
def question_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    questions: fixture_dependencies.drivers.refs.Questions,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.question_contexts.QuestionObservationContext:
    """Return services for question observations.

    Returns:
        Services for question observations.

    """
    return fixture_dependencies.contexts.question_contexts.QuestionObservationContext(
        client, turns, questions, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def question_interaction_context(
    client: fixture_dependencies.harness.BaqylauClient,
    questions: fixture_dependencies.drivers.refs.Questions,
    controls: fixture_dependencies.drivers.refs.Controls,
    turns: fixture_dependencies.drivers.refs.Turns,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.question_contexts.QuestionInteractionContext:
    """Return services for question interactions.

    Returns:
        Services for question interactions.

    """
    return fixture_dependencies.contexts.question_contexts.QuestionInteractionContext(
        client, questions, controls, turns, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def plan_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    plans: fixture_dependencies.drivers.refs.Plans,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.planning_contexts.PlanObservationContext:
    """Return services for plan observations.

    Returns:
        Services for plan observations.

    """
    return fixture_dependencies.contexts.planning_contexts.PlanObservationContext(client, turns, plans, wait_policy)
