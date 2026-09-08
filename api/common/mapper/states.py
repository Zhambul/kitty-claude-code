# Copyright (c) 2026 Zhambyl Yermagambet
"""Map repository and terminal state to API models."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.models.values.repository_status import RepositoryStatusResponse
from api.common.models.values.terminal_state import (
    TerminalInputStateResponse,
    TerminalStateResponse,
)

if TYPE_CHECKING:
    from core.git_status import RepositoryStatus
    from harness.models.probe import (
        TerminalSessionState,
    )


def terminal_state(terminal_session_state: TerminalSessionState) -> TerminalStateResponse:
    """Map terminal state to its API model.

    Returns:
        The terminal state response.

    """
    return TerminalStateResponse(
        window_id=terminal_session_state.window_id,
        input_state=(
            None
            if terminal_session_state.input_state is None
            else TerminalInputStateResponse(
                typed_text=terminal_session_state.input_state.typed_text,
                suggestion=terminal_session_state.input_state.suggestion,
            )
        ),
    )


def maybe_repository_status(
    repository_status: RepositoryStatus | None,
) -> RepositoryStatusResponse | None:
    """Map repository status when it exists.

    Returns:
        The repository status response, or ``None``.

    """
    if repository_status is None:
        return None
    return RepositoryStatusResponse(
        branch=repository_status.branch,
        worktree=repository_status.worktree,
        dirty=repository_status.dirty,
    )
