# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture catalogs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e import (
    e2e_fixture_actors,
    e2e_fixture_dependencies as fixture_dependencies,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


@fixture_dependencies.application.pytest.fixture
def plan_interaction_context(
    client: fixture_dependencies.harness.BaqylauClient,
    plans: fixture_dependencies.drivers.refs.Plans,
    controls: fixture_dependencies.drivers.refs.Controls,
    turns: fixture_dependencies.drivers.refs.Turns,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.planning_contexts.PlanInteractionContext:
    """Return services for plan interactions.

    Returns:
        Services for plan interactions.

    """
    return fixture_dependencies.contexts.planning_contexts.PlanInteractionContext(
        client, plans, controls, turns, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def task_naming_context(
    client: fixture_dependencies.harness.BaqylauClient,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    tasks: fixture_dependencies.drivers.refs.Tasks,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.contexts.planning_contexts.TaskNamingContext:
    """Return services for task naming.

    Returns:
        Services for task naming.

    """
    return fixture_dependencies.contexts.planning_contexts.TaskNamingContext(client, sessions, tasks, wait_policy)


def finish_scenario_sessions(
    client: fixture_dependencies.harness.BaqylauClient,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> None:
    """Close live scenario sessions and wait for all sessions to finish."""
    for session in sessions.all_references():
        snapshot = client.sessions.snapshot(session)
        if snapshot.session_data.session.state != "finished" and snapshot.session_data.live:
            receipt = client.sessions.close(session)
            assert receipt.status_code in {200, 202}, (
                f"cleanup action {receipt.request_id!r} was not accepted: {receipt.outcome}"
            )
        client.sessions.wait_until_finished(session, wait_policy.cleanup)


def restart_application(
    application_process: fixture_dependencies.drivers.process_testkit.ApplicationProcess,
    client: fixture_dependencies.harness.BaqylauClient,
) -> None:
    """Restart the test application and wait until it is ready."""
    application_process.restart()
    client.application.wait_until_ready()


@fixture_dependencies.application.pytest.fixture(autouse=True)
def stalled_scenario_report(
    request: fixture_dependencies.application.pytest.FixtureRequest,
    application_process: fixture_dependencies.drivers.process_testkit.ApplicationProcess,
) -> Iterator[None]:
    """Print live evidence after one minute with no stored progress."""
    stop_event = fixture_dependencies.application.threading.Event()
    reporter = fixture_dependencies.application.threading.Thread(
        target=e2e_fixture_actors.report_stalls, args=(stop_event, application_process, request.node), daemon=True,
    )
    reporter.start()
    try:
        yield
    finally:
        stop_event.set()
        reporter.join(timeout=1)


@fixture_dependencies.application.pytest.fixture
def session_control_context(
    session_prompt_context: fixture_dependencies.testkit.session_contexts.SessionPromptContext,
    controls: fixture_dependencies.drivers.refs.Controls,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.testkit.session_contexts.SessionControlContext:
    """Return prompt delivery services and control references.

    Returns:
        Prompt delivery services and control references.

    """
    return fixture_dependencies.testkit.session_contexts.SessionControlContext(
        session_prompt_context, controls, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def session_continuation_context(
    session_prompt_context: fixture_dependencies.testkit.session_contexts.SessionPromptContext,
    session_continuations: fixture_dependencies.drivers.refs.SessionContinuations,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.testkit.session_contexts.SessionContinuationContext:
    """Return services for a continued session.

    Returns:
        Services for a continued session.

    """
    return fixture_dependencies.testkit.session_contexts.SessionContinuationContext(
        session_prompt_context, session_continuations, wait_policy,
    )
