# Copyright (c) 2026 Zhambyl Yermagambet
"""Define E2E references that describe a session timeline."""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum

from api.application.models.resume.resumable_session_response import ResumableSessionResponse
from sdk.client import SessionRef


@dataclass(frozen=True)
class SessionSpec:
    """Represent the requested session configuration."""

    harness: str
    model: str
    effort: str
    workspace: str | None = None
    account_id: str | None = None


@dataclass(frozen=True)
class AccountSelectionRef:
    """Represent one selected account."""

    account_id: str
    display_name: str


@dataclass(frozen=True)
class SessionContinuationRef:
    """Represent a session before and after continuation."""

    before: SessionRef
    after: SessionRef
    saved: ResumableSessionResponse | None = None


class JourneyOrigin(StrEnum):
    """Identify the process that starts a journey."""

    DASHBOARD = "dashboard"
    TERMINAL = "terminal"


@dataclass(frozen=True)
class SessionJourneyRef:
    """Represent one session terminal journey."""

    session: SessionRef
    origin: JourneyOrigin
    window_id: str


@dataclass(frozen=True)
class TurnRef:
    """Represent one session turn."""

    session: SessionRef
    prompt: str
    cursor_before: int
    expected_prompt_count: int
    actor_id: str | None = None
    turn_id: str | None = None
    prompt_cursor: int | None = None
    prompt_message_id: str | None = None
    completion_after_cursor: int | None = None
    start_cursor: int | None = None
    attachment_paths: tuple[str, ...] = ()
    native_attachment_names: tuple[str, ...] = ()

    @property
    def activity_cursor(self) -> int | None:
        """Read the first visible event cursor for this turn."""
        return self.prompt_cursor if self.start_cursor is None else self.start_cursor

    def resumed_after(self, cursor: int) -> TurnRef:
        """Require the next completion after one control action.

        Returns:
            A copy of this reference with the supplied completion boundary.

        """
        return replace(self, completion_after_cursor=cursor)


@dataclass(frozen=True)
class ShellRef:
    """Represent one shell operation."""

    session: SessionRef
    shell_id: str
    actor_id: str
