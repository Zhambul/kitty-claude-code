# Copyright (c) 2026 Zhambyl Yermagambet
"""Status and color checks shared by dashboard and terminal journeys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import given, parsers, then

from domain.actor_state import ActorStatus
from sdk.client import BaqylauClient, wait_for
from terminal.theme import tab_appearance
from tests.e2e.testkit import status_checks

if TYPE_CHECKING:
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import SessionJourneys, Sessions
    from tests.e2e.testkit.repository import RepositoryWorkspace
    from tests.e2e.testkit.status_colors import KittyTabColorReader


@given("the isolated repository has a blocking Claude Stop hook")
def install_blocking_stop_hook(
    repository_workspace: RepositoryWorkspace,
) -> None:
    """Process install blocking stop hook."""
    repository_workspace.install_blocking_stop_hook()


@then("the blocking Claude Stop hook starts")
def blocking_stop_hook_starts(
    repository_workspace: RepositoryWorkspace,
    wait_policy: WaitPolicy,
) -> None:
    """Process blocking stop hook starts."""
    marker = repository_workspace.blocking_stop_marker
    wait_for(
        "the blocking Claude Stop hook to start",
        lambda: True if marker.exists() else None,
        timeout=wait_policy.turn,
    )


@then(
    parsers.parse(
        'the blocked Stop hook feedback starts a new turn in session "{name}"',
    ),
)
def blocked_stop_feedback_starts_new_turn(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    name: str,
) -> None:
    """Process blocked stop feedback starts new turn."""
    wait_for(
        f"session {name!r} Stop hook feedback to start a new turn",
        status_checks.StopFeedbackCheck(client, sessions.get(name)),
        timeout=wait_policy.turn,
    )


@then(
    parsers.parse(
        'the terminal tab for journey session "{name}" has color {status}',
    ),
)
def terminal_tab_has_status_color(
    session_journeys: SessionJourneys,
    terminal_color_reader: KittyTabColorReader,
    wait_policy: WaitPolicy,
    name: str,
    status: str,
) -> None:
    """Process terminal tab has status color."""
    journey = session_journeys.get(name)
    terminal_color_reader.wait_for(
        journey.window_id,
        tab_appearance(ActorStatus(status)),
        wait_policy.feed,
    )


@then(
    parsers.parse(
        'for {seconds:d} seconds the terminal tab for journey session "{name}" does not have color {status}',
    ),
)
def terminal_tab_does_not_have_status_color(
    session_journeys: SessionJourneys,
    terminal_color_reader: KittyTabColorReader,
    name: str,
    status: str,
    seconds: int,
) -> None:
    """Process terminal tab does not have status color."""
    journey = session_journeys.get(name)
    terminal_color_reader.assert_not_seen_for(
        journey.window_id,
        tab_appearance(ActorStatus(status)),
        seconds,
    )


@then(parsers.parse('the lead in session "{name}" has status {status}'))
def session_lead_has_status(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    name: str,
    status: str,
) -> None:
    """Process session lead has status."""
    expected = ActorStatus(status)
    wait_for(
        f"session {name!r} lead to have status {status!r}",
        lambda: True if status_checks.lead_has_status(client, sessions, name, expected) else None,
        timeout=wait_policy.feed,
    )
