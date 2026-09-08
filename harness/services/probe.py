# Copyright (c) 2026 Zhambyl Yermagambet
"""What a live session's own TUI is showing right now.

The one reader of a harness's `composer`: it resolves the session's
window from a raw event, then lets the harness read its own input line off that
window's screen. A session that is not on screen simply has no input state.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.models.probe import (
    TerminalInputState,
    TerminalSessionState,
)
from harness.services.terminal_driver import TerminalDriver

if TYPE_CHECKING:
    from domain.ids import SessionId
    from repository.contract.sessions import SessionRepository
    from terminal.adapter import TerminalAdapter
    from terminal.contract import TerminalPlugin


class TerminalInputService:
    """Represent terminal input service."""

    def __init__(
        self,
        session_repository: SessionRepository,
        terminal_adapter: TerminalAdapter,
        terminal_plugin: TerminalPlugin,
    ) -> None:
        """Initialize the object."""
        self.sessions = session_repository
        self.terminal = terminal_adapter
        self.plugin = terminal_plugin
        self.driver = TerminalDriver(terminal_plugin)

    def read(self, session_id: SessionId) -> TerminalInputState | None:
        """Return read.

        Returns:
            Read.

        """
        return self.state(session_id).input_state

    def state(self, session_id: SessionId) -> TerminalSessionState:
        """Return the state.

        Returns:
            State.

        """
        window_id = self.terminal.window_for_session(session_id)
        session = self.sessions.find(session_id)
        plugin = None if session is None else session.plugin
        input_state = (
            plugin.composer.read(self.driver, window_id)
            if window_id is not None and plugin is not None and plugin.composer is not None
            else None
        )
        return TerminalSessionState(window_id, input_state)
