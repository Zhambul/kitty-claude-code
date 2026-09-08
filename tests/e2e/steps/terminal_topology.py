# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that verify terminal pane topology."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

if TYPE_CHECKING:
    from tests.e2e.testkit.references import SessionJourneys
    from tests.e2e.testkit.terminals import RealTerminalDriver


@then(parsers.parse('journey session "{session_name}" has its exact terminal pane set'))
def session_has_exact_terminal_panes(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
) -> None:
    """Verify the session pane set."""
    real_terminal_driver.wait_for_panes(session_journeys[session_name])


@then(parsers.parse('journey session "{session_name}" has no auxiliary terminal panes'))
def session_has_no_auxiliary_panes(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
) -> None:
    """Verify the session has no auxiliary panes."""
    real_terminal_driver.wait_for_no_auxiliary_panes(session_journeys[session_name])


@then(parsers.parse('journey session "{session_name}" keeps its shell tab'))
def session_keeps_shell_tab(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
) -> None:
    """Verify the session host window still exists."""
    real_terminal_driver.assert_host_window_exists(session_journeys[session_name])
