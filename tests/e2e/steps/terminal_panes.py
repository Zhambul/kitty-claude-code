# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that change and check activity panes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.references import SessionJourneys
    from tests.e2e.testkit.terminals import RealTerminalDriver


@when(parsers.parse('I toggle journey session "{session_name}" terminal panes'))
def toggle_terminal_panes(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
) -> None:
    """Toggle the session activity panes."""
    real_terminal_driver.toggle(session_journeys.get(session_name))


@when(parsers.parse('I grow journey session "{session_name}" activity pane by {columns:d} columns'))
def grow_activity_pane(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    columns: int,
) -> None:
    """Grow the session activity pane."""
    real_terminal_driver.grow(session_journeys.get(session_name), columns)


@when(parsers.parse('I shrink journey session "{session_name}" activity pane by {columns:d} columns'))
def shrink_activity_pane(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    columns: int,
) -> None:
    """Shrink the session activity pane."""
    real_terminal_driver.shrink(session_journeys.get(session_name), columns)


@when(parsers.parse('I set journey session "{session_name}" activity pane to {percent:d} percent'))
def set_activity_pane_percent(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    percent: int,
) -> None:
    """Set the session activity pane width."""
    real_terminal_driver.set_percent(session_journeys.get(session_name), percent)


@when(parsers.parse('I reset journey session "{session_name}" activity pane width'))
def reset_activity_pane_percent(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
) -> None:
    """Reset the session activity pane width."""
    real_terminal_driver.reset(session_journeys.get(session_name))


@then(parsers.parse('journey session "{session_name}" activity pane uses {percent:d} percent'))
def activity_pane_uses_percent(
    real_terminal_driver: RealTerminalDriver,
    session_journeys: SessionJourneys,
    session_name: str,
    percent: int,
) -> None:
    """Verify the session activity pane width."""
    real_terminal_driver.wait_for_percent(session_journeys.get(session_name), percent)
