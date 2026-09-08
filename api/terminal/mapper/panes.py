# Copyright (c) 2026 Zhambyl Yermagambet
"""A pane command's outcome to the gesture's reply model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.terminal.models.panes.pane_command_response import PaneCommandResponse

if TYPE_CHECKING:
    from terminal.panes.commands import PaneCommandOutcome


def pane_command(pane_command_outcome: PaneCommandOutcome) -> PaneCommandResponse:
    """Return the pane command.

    Returns:
        Pane command.

    """
    return PaneCommandResponse(
        handled=pane_command_outcome.handled,
        succeeded=pane_command_outcome.succeeded,
        reason=pane_command_outcome.reason,
    )
