# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that save and compare pane geometry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.observation_contexts import TerminalGeometryContext
    from tests.e2e.testkit.references import References, SessionJourneys
    from tests.e2e.testkit.terminal_models import PaneGeometry
    from tests.e2e.testkit.terminals import RealTerminalDriver


@when(parsers.parse('I remember journey session "{session_name}" pane geometry as "{geometry_name}"'))
def remember_pane_geometry(
    real_terminal_driver: RealTerminalDriver,
    terminal_pane_geometries: References[PaneGeometry],
    session_journeys: SessionJourneys,
    session_name: str,
    geometry_name: str,
) -> None:
    """Save one session pane geometry."""
    terminal_pane_geometries.bind(
        geometry_name,
        real_terminal_driver.wait_for_panes(session_journeys.get(session_name)).geometry,
    )


@then(parsers.parse('journey session "{session_name}" activity pane is {direction} than "{geometry_name}"'))
def activity_pane_has_width_change(
    terminal_geometry_context: TerminalGeometryContext,
    session_name: str,
    direction: str,
    geometry_name: str,
) -> None:
    """Verify the activity pane changed width.

    Raises:
        AssertionError: If the requested direction is unknown.

    """
    if direction not in {"wider", "narrower"}:
        message = f"unknown pane width direction {direction!r}"
        raise AssertionError(message)
    terminal_geometry_context.driver.wait_for_width_change(
        terminal_geometry_context.journeys.get(session_name),
        terminal_geometry_context.geometries.get(geometry_name),
        direction,
    )
