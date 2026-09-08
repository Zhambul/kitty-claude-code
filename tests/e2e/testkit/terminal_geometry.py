# Copyright (c) 2026 Zhambyl Yermagambet
"""Observe terminal pane geometry changes for E2E journeys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.e2e.testkit.terminal_topology import pane_set

if TYPE_CHECKING:
    from terminal.contract import TerminalPlugin
    from tests.e2e.testkit.references import SessionJourneyRef
    from tests.e2e.testkit.terminal_models import PaneGeometry


def width_change(
    terminal: TerminalPlugin,
    journey: SessionJourneyRef,
    before: PaneGeometry,
    direction: str,
    observed: list[PaneGeometry],
) -> PaneGeometry | None:
    """Return the geometry after it changes in the requested direction.

    Returns:
        The geometry after it changes in the requested direction.

    """
    found = pane_set(terminal, journey)
    if found is None:
        return None
    observed.clear()
    observed.append(found.geometry)
    changed = (
        found.activity.columns > before.activity_columns
        if direction == "wider"
        else found.activity.columns < before.activity_columns
    )
    return found.geometry if changed else None


def geometry_with_percent(
    terminal: TerminalPlugin,
    journey: SessionJourneyRef,
    percent: int,
) -> PaneGeometry | None:
    """Return the geometry when it has the requested percent.

    Returns:
        The geometry when it has the requested percent.

    """
    found = pane_set(terminal, journey)
    if found is None or found.geometry.percent != percent:
        return None
    return found.geometry


def width_change_description(direction: str, before: PaneGeometry, observed: list[PaneGeometry]) -> str:
    """Describe the width change that the wait operation needs.

    Returns:
        The requested direction, original geometry, and latest observation.

    """
    last_observation: PaneGeometry | str = observed[-1] if observed else "no complete pane set"
    return f"activity pane to become {direction} than {before}; observed {last_observation}"
