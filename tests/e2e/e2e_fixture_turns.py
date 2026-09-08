# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture turns."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies

if TYPE_CHECKING:
    from collections.abc import Iterator

FILE_OPERATION_FIXTURE = "baqylau-e2e-file.txt"


@fixture_dependencies.application.pytest.fixture
def journey_continue_context(
    journey_driver: fixture_dependencies.contexts.JourneyDriver,
    session_journeys: fixture_dependencies.drivers.refs.SessionJourneys,
    turns: fixture_dependencies.drivers.refs.Turns,
) -> fixture_dependencies.harness.journey_contexts.JourneyContinueContext:
    """Return services that continue journey sessions.

    Returns:
        Services that continue journey sessions.

    """
    return fixture_dependencies.harness.journey_contexts.JourneyContinueContext(journey_driver, session_journeys, turns)


@fixture_dependencies.application.pytest.fixture
def journey_resume_context(
    journey_driver: fixture_dependencies.contexts.JourneyDriver,
    session_journeys: fixture_dependencies.drivers.refs.SessionJourneys,
    session_continuations: fixture_dependencies.drivers.refs.SessionContinuations,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    turns: fixture_dependencies.drivers.refs.Turns,
) -> fixture_dependencies.harness.journey_contexts.JourneyResumeContext:
    """Return services that resume journey sessions.

    Returns:
        Services that resume journey sessions.

    """
    return fixture_dependencies.harness.journey_contexts.JourneyResumeContext(
        journey_driver, session_journeys, session_continuations, sessions, turns,
    )


@fixture_dependencies.application.pytest.fixture
def session_launch_references(
    session_specs: fixture_dependencies.drivers.refs.SessionSpecs,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    turns: fixture_dependencies.drivers.refs.Turns,
) -> fixture_dependencies.drivers.launching.SessionLaunchReferences:
    """Return references that a session launch updates.

    Returns:
        References that a session launch updates.

    """
    return fixture_dependencies.drivers.launching.SessionLaunchReferences(session_specs, sessions, turns)


@fixture_dependencies.application.pytest.fixture
def skill_fixtures(workspace: str) -> Iterator[fixture_dependencies.contexts.skill_testkit.SkillFixtures]:
    """Create test skill files and remove them after the test.

    Yields:
        The skill file manager for the workspace.

    """
    fixtures = fixture_dependencies.contexts.skill_testkit.SkillFixtures(workspace)
    try:
        yield fixtures
    finally:
        fixtures.close()


@fixture_dependencies.application.pytest.fixture
def terminal_geometry_context(
    real_terminal_driver: fixture_dependencies.testkit.terminal_testkit.RealTerminalDriver,
    terminal_pane_geometries: fixture_dependencies.drivers.refs.References[
        fixture_dependencies.testkit.terminal_models.PaneGeometry
    ],
    session_journeys: fixture_dependencies.drivers.refs.SessionJourneys,
) -> fixture_dependencies.drivers.observation_contexts.TerminalGeometryContext:
    """Return services for terminal geometry observations.

    Returns:
        Services for terminal geometry observations.

    """
    return fixture_dependencies.drivers.observation_contexts.TerminalGeometryContext(
        real_terminal_driver, terminal_pane_geometries, session_journeys,
    )


@fixture_dependencies.application.pytest.fixture
def global_stream_observation_context(
    global_stream_updates: fixture_dependencies.drivers.refs.GlobalStreamUpdates,
    stream_checkpoints: fixture_dependencies.drivers.refs.StreamCheckpoints,
    sessions: fixture_dependencies.drivers.refs.Sessions,
) -> fixture_dependencies.drivers.observation_contexts.GlobalStreamObservationContext:
    """Return references for global stream observations.

    Returns:
        References for global stream observations.

    """
    return fixture_dependencies.drivers.observation_contexts.GlobalStreamObservationContext(
        global_stream_updates, stream_checkpoints, sessions,
    )


@fixture_dependencies.application.pytest.fixture
def file_operation_path(workspace: str) -> Iterator[str]:
    """Keep a test file path clear before and after the test.

    Yields:
        The workspace path reserved for file-operation checks.

    """
    path = str(fixture_dependencies.application.Path(workspace) / FILE_OPERATION_FIXTURE)
    fixture_dependencies.application.Path(path).unlink(missing_ok=True)
    try:
        yield path
    finally:
        fixture_dependencies.application.Path(path).unlink(missing_ok=True)
