# Copyright (c) 2026 Zhambyl Yermagambet
"""Build commands for terminal pane clients."""

from core import clients
from domain.ids import SessionId

PANE_CLIENT = "terminal_pane.py"


def command(kind: str, session_id: SessionId) -> tuple[str, ...]:
    """Return the command for one terminal pane.

    Returns:
        The pane command.

    """
    return clients.command(PANE_CLIENT, session_id, kind)
