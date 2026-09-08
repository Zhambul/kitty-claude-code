# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the panes module."""

# api/terminal/panes.py — the pane keybinding gestures, one endpoint per
# command (the URL is the discriminator; the old single endpoint took a
# `command` field).
from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from fastapi import APIRouter, Response

from api.responses import with_body
from api.terminal.mapper import panes as mapper
from api.terminal.models.panes import (
    grow_request,
    pane_command_response,
    reset_request,
    set_percent_request,
    shrink_request,
    toggle_request,
)
from app.provider_terminal import PaneCommands
from domain.ids import WindowId

if TYPE_CHECKING:
    from api.terminal.models.panes.pane_gesture_request import PaneGestureRequest
    from terminal.panes.commands import PaneCommandOutcome

router = APIRouter()

# Same rule as the control plane: the verdict is the status, the body is
# unchanged. `handled=False` (no session in this window) is a 200 — nothing was
# asked of the terminal; a 409 is the terminal refusing.
PANE_RESPONSES = with_body(
    pane_command_response.PaneCommandResponse,
    {
        409: "Handled by this window's session, and the terminal refused it.",
    },
)


def _window_id(pane_gesture_request: PaneGestureRequest) -> WindowId | None:
    return WindowId(pane_gesture_request.window_id) if pane_gesture_request.window_id else None


def _respond(
    pane_command_outcome: PaneCommandOutcome,
    response: Response,
) -> pane_command_response.PaneCommandResponse:
    """Respond.

    The status is set ON the injected response, so the handler can return the
        reply model itself rather than a hand-serialized copy of it.

    Returns:
        The pane command response.

    """
    response.status_code = (
        HTTPStatus.CONFLICT if pane_command_outcome.handled and not pane_command_outcome.succeeded else HTTPStatus.OK
    )
    return mapper.pane_command(pane_command_outcome)


@router.post("/api/terminal/panes/toggle", responses=PANE_RESPONSES)
def toggle_panes(
    toggle_panes_request: toggle_request.TogglePanesRequest,
    panes: PaneCommands,
    response: Response,
) -> pane_command_response.PaneCommandResponse:
    """Toggle panes.

    Returns:
        The pane command response.

    """
    outcome = panes.toggle(_window_id(toggle_panes_request), toggle_panes_request.working_directory)
    return _respond(outcome, response)


@router.post("/api/terminal/panes/grow", responses=PANE_RESPONSES)
def grow_pane(
    grow_pane_request: grow_request.GrowPaneRequest,
    panes: PaneCommands,
    response: Response,
) -> pane_command_response.PaneCommandResponse:
    """Grow pane.

    Returns:
        The pane command response.

    """
    outcome = panes.grow(
        _window_id(grow_pane_request),
        grow_pane_request.working_directory,
        grow_pane_request.columns,
    )
    return _respond(outcome, response)


@router.post("/api/terminal/panes/shrink", responses=PANE_RESPONSES)
def shrink_pane(
    shrink_pane_request: shrink_request.ShrinkPaneRequest,
    panes: PaneCommands,
    response: Response,
) -> pane_command_response.PaneCommandResponse:
    """Shrink pane.

    Returns:
        The pane command response.

    """
    outcome = panes.shrink(
        _window_id(shrink_pane_request),
        shrink_pane_request.working_directory,
        shrink_pane_request.columns,
    )
    return _respond(outcome, response)


@router.post("/api/terminal/panes/reset", responses=PANE_RESPONSES)
def reset_pane(
    reset_pane_request: reset_request.ResetPaneRequest,
    panes: PaneCommands,
    response: Response,
) -> pane_command_response.PaneCommandResponse:
    """Reset pane.

    Returns:
        The pane command response.

    """
    outcome = panes.reset(_window_id(reset_pane_request), reset_pane_request.working_directory)
    return _respond(outcome, response)


@router.post("/api/terminal/panes/set-percent", responses=PANE_RESPONSES)
def set_pane_percent(
    set_pane_percent_request: set_percent_request.SetPanePercentRequest,
    panes: PaneCommands,
    response: Response,
) -> pane_command_response.PaneCommandResponse:
    """Set pane percent.

    Returns:
        The pane command response.

    """
    outcome = panes.set_percent(
        _window_id(set_pane_percent_request),
        set_pane_percent_request.working_directory,
        set_pane_percent_request.percent,
    )
    return _respond(outcome, response)
