# Copyright (c) 2026 Zhambyl Yermagambet
"""Synchronize one terminal composer with durable workspace state."""

import threading
from collections.abc import Callable

from app.session_application_resources import TerminalSessionReader
from domain.composer import ComposerDraft
from domain.ids import SessionId
from harness.models.probe import (
    TerminalSessionState,
)
from harness.services.terminal_gate import SessionTerminalGate
from repository.contract.workspace import SessionWorkspaceRepository


class TerminalDraftSync:
    """Read terminal state and copy changed drafts to workspace storage."""

    def __init__(
        self,
        terminal_session_reader: TerminalSessionReader,
        session_workspace_repository: SessionWorkspaceRepository,
        session_terminal_gate: SessionTerminalGate,
        clock: Callable[[], float],
    ) -> None:
        """Initialize the synchronizer."""
        self.terminal_reader = terminal_session_reader
        self.workspaces = session_workspace_repository
        self.terminal_gate = session_terminal_gate
        self.clock = clock
        self._terminal_text: dict[SessionId, str] = {}
        self._terminal_text_lock = threading.Lock()

    def state(self, session_id: SessionId, *, attention_pending: bool) -> TerminalSessionState:
        """Read native input state and synchronize a visible composer.

        Returns:
            The terminal state, with input state omitted while attention is pending.

        """
        with self.terminal_gate.enter(session_id):
            terminal_state = self.terminal_reader.state(session_id)
            if attention_pending:
                return TerminalSessionState(terminal_state.window_id, None)
            self._synchronize(session_id, terminal_state)
            return terminal_state

    def _synchronize(self, session_id: SessionId, terminal_session_state: TerminalSessionState) -> None:
        input_state = terminal_session_state.input_state
        if input_state is None or input_state.typed_text is None:
            return
        text = input_state.typed_text
        if not self._changed(session_id, text):
            return
        workspace = self.workspaces.find(session_id)
        draft = None if workspace is None else workspace.draft
        if text:
            self.workspaces.save_composer_draft(
                session_id,
                ComposerDraft(text, "terminal", self.clock() * 1000),
            )
        elif draft is not None and draft.origin == "terminal":
            self.workspaces.save_composer_draft(
                session_id,
                ComposerDraft("", "terminal", self.clock() * 1000),
            )

    def _changed(self, session_id: SessionId, text: str) -> bool:
        with self._terminal_text_lock:
            if session_id in self._terminal_text and self._terminal_text.get(session_id) == text:
                return False
            self._terminal_text[session_id] = text
            return True
