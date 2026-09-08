# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that start, continue, and resume journey sessions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

from tests.e2e.testkit.references import JourneyOrigin

if TYPE_CHECKING:
    from tests.e2e.testkit import journey_contexts


def journey_origin(origin_name: str) -> JourneyOrigin:
    """Return one recognized journey origin.

    Returns:
        The recognized origin.

    Raises:
        AssertionError: If the origin name is unknown.

    """
    try:
        return JourneyOrigin(origin_name)
    except ValueError as error:
        message = f"unknown journey origin {origin_name!r}"
        raise AssertionError(message) from error


@when(parsers.parse('I start journey session "{session_name}" from the {origin} as turn "{turn_name}" with prompt'))
def start_journey_session(
    journey_start_context: journey_contexts.JourneyStartContext,
    session_name: str,
    origin: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Start one journey session."""
    started = journey_start_context.driver.start(
        journey_start_context.session_specs.get(session_name),
        journey_origin(origin),
        docstring.strip(),
    )
    journey_start_context.journeys.bind(session_name, started.journey)
    journey_start_context.sessions.bind(session_name, started.journey.session)
    journey_start_context.turns.bind(turn_name, started.turn)


@when(parsers.parse('I continue journey session "{session_name}" from the {origin} as turn "{turn_name}" with prompt'))
def continue_journey_session(
    journey_continue_context: journey_contexts.JourneyContinueContext,
    session_name: str,
    origin: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Continue one journey session."""
    continued = journey_continue_context.driver.continue_session(
        journey_continue_context.journeys.get(session_name), journey_origin(origin), docstring.strip(),
    )
    journey_continue_context.journeys.replace(session_name, continued.journey)
    journey_continue_context.turns.bind(turn_name, continued.turn)


@when(
    parsers.parse(
        'I start journey session "{new_name}" with native /new in journey session '
        '"{old_name}" as turn "{turn_name}" with prompt',
    ),
)
def start_new_native_journey_session(
    journey_start_context: journey_contexts.JourneyStartContext,
    new_name: str,
    old_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Start a native child journey session."""
    started = journey_start_context.driver.start_new_native_session(
        journey_start_context.journeys.get(old_name), docstring.strip(),
    )
    journey_start_context.journeys.bind(new_name, started.journey)
    journey_start_context.sessions.bind(new_name, started.journey.session)
    journey_start_context.turns.bind(turn_name, started.turn)


@when(
    parsers.parse(
        'I run unattended session "{detached_name}" with the terminal environment '
        'from journey session "{host_name}" and prompt',
    ),
)
def run_unattended_session_with_host_environment(
    journey_start_context: journey_contexts.JourneyStartContext,
    detached_name: str,
    host_name: str,
    docstring: str,
) -> None:
    """Run an unattended session with a journey terminal environment."""
    journey_start_context.sessions.bind(
        detached_name,
        journey_start_context.driver.run_unattended_with_inherited_window(
            journey_start_context.session_specs.get(detached_name),
            journey_start_context.journeys.get(host_name),
            docstring.strip(),
        ),
    )


@when(parsers.parse('I resume journey session "{session_name}" from the {origin} as turn "{turn_name}" with prompt'))
def resume_journey_session(
    journey_resume_context: journey_contexts.JourneyResumeContext,
    session_name: str,
    origin: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Resume one journey session."""
    resumed = journey_resume_context.driver.resume(
        journey_resume_context.journeys.get(session_name), journey_origin(origin), docstring.strip(),
    )
    journey_resume_context.journeys.replace(session_name, resumed.journey)
    journey_resume_context.continuations.bind(session_name, resumed.continuation)
    journey_resume_context.sessions.replace(session_name, resumed.journey.session)
    journey_resume_context.turns.bind(turn_name, resumed.turn)
