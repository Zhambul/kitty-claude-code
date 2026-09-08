# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that operate a journey terminal."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from sdk.client import BaqylauClient, wait_for

if TYPE_CHECKING:
    from tests.e2e.testkit import policy
    from tests.e2e.testkit.journeys import JourneyDriver
    from tests.e2e.testkit.references import SessionJourneyRef, SessionJourneys


def journey_draft_matches(client: BaqylauClient, journey: SessionJourneyRef, text: str) -> bool | None:
    """Return true once terminal draft text matches.

    Returns:
        ``True`` on a match, otherwise ``None``.

    """
    input_state = client.preferences.session_state(journey.session).terminal.input_state
    return True if input_state is not None and input_state.typed_text == text else None


@when(parsers.parse('I close the terminal for journey session "{session_name}"'))
def close_journey_terminal(journey_driver: JourneyDriver, session_journeys: SessionJourneys, session_name: str) -> None:
    """Close one journey terminal."""
    journey_driver.stop_terminal(session_journeys[session_name])


@when(parsers.parse("I submit native command '{command}' to journey session \"{session_name}\""))
def submit_native_journey_command(
    journey_driver: JourneyDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    command: str,
) -> None:
    """Submit one native terminal command."""
    journey_driver.submit_native_command(session_journeys.get(session_name), command)


@when(parsers.parse("I insert terminal draft '{text}' in journey session \"{session_name}\""))
def insert_journey_terminal_draft(
    journey_driver: JourneyDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    text: str,
) -> None:
    """Insert text into one journey terminal draft."""
    journey_driver.insert_terminal_draft(session_journeys.get(session_name), text)


@when(parsers.parse('I put journey session "{session_name}" in {mode} editor mode'))
def set_journey_editor_mode(
    journey_driver: JourneyDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    mode: str,
) -> None:
    """Set one journey editor mode.

    Raises:
        AssertionError: If the editor mode is unknown.

    """
    if mode == "standard":
        return
    if mode != "visual":
        message = f"unknown editor mode {mode!r}"
        raise AssertionError(message)
    journey_driver.use_visual_editor_mode(session_journeys.get(session_name))


@then(parsers.re(r'journey session "(?P<session_name>[^"]+)" terminal draft is exactly \'(?P<text>.*)\''))
def journey_terminal_draft_is_exact(
    client: BaqylauClient,
    session_journeys: SessionJourneys,
    wait_policy: policy.WaitPolicy,
    session_name: str,
    text: str,
) -> None:
    """Verify one journey terminal draft."""
    journey = session_journeys.get(session_name)
    wait_for(
        f"journey session {session_name!r} terminal draft to equal {text!r}",
        partial(journey_draft_matches, client, journey, text),
        timeout=wait_policy.feed,
    )


@when(parsers.parse('I interrupt journey session "{session_name}" from its terminal'))
def interrupt_journey_session_from_terminal(
    journey_driver: JourneyDriver,
    session_journeys: SessionJourneys,
    session_name: str,
) -> None:
    """Interrupt a journey session from its terminal."""
    journey_driver.interrupt_from_terminal(session_journeys.get(session_name))
