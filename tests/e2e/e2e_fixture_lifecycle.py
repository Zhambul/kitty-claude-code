# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture lifecycle."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def question_work_context(
    question_work_driver: fixture_dependencies.drivers.QuestionWorkDriver,
    session_specs: fixture_dependencies.drivers.refs.SessionSpecs,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    turns: fixture_dependencies.drivers.refs.Turns,
    works: fixture_dependencies.drivers.refs.Works,
) -> fixture_dependencies.contexts.question_contexts.QuestionWorkContext:
    """Return services for question work.

    Returns:
        Services for question work.

    """
    return fixture_dependencies.contexts.question_contexts.QuestionWorkContext(
        question_work_driver, session_specs, sessions, turns, works,
    )


@fixture_dependencies.application.pytest.fixture
def skill_launch_context(
    skill_work_driver: fixture_dependencies.contexts.skill_testkit.SkillWorkDriver,
    session_specs: fixture_dependencies.drivers.refs.SessionSpecs,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    turns: fixture_dependencies.drivers.refs.Turns,
    works: fixture_dependencies.drivers.refs.Works,
) -> fixture_dependencies.drivers.action_contexts.SkillLaunchContext:
    """Return services for skill work launches.

    Returns:
        Services for skill work launches.

    """
    return fixture_dependencies.drivers.action_contexts.SkillLaunchContext(
        skill_work_driver, session_specs, sessions, turns, works,
    )
