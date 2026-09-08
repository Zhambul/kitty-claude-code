# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared fixtures and builders for canonical harness tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.models.controls import (
    ControlContext,
    TitleWriteOutcome,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.support_hooks import DEFAULT_CONTROL_WINDOW_ID

if TYPE_CHECKING:
    from domain import event_work, ids as domain_ids
    from harness.models.session import (
        Session,
    )
    from terminal.contract import TerminalPlugin


def control_context(
    session: Session,
    terminal: TerminalPlugin,
    pending_attention: event_work.QuestionAsked | event_work.PlanProposed | None = None,
    window_id: domain_ids.WindowId | None = DEFAULT_CONTROL_WINDOW_ID,
    *,
    lead_active: bool = False,
) -> ControlContext:
    """Build a control context for a test session.

    Returns:
        The context with the supplied terminal and attention state.

    """
    return ControlContext(session, terminal, window_id, None, lead_active, pending_attention)


def claude_composer_screen(text: str = "") -> str:
    """Build a Claude composer screen with the supplied draft text.

    Returns:
        The screen text with prompt and divider escape sequences.

    """
    divider = fixture.GREY_ANSI_SEQUENCE + fixture.DIVIDER_CHARACTER * fixture.DIVIDER_WIDTH
    return f"{divider}\n\x1b[m\u276f\xa0{text}\n{divider}"


class RecordingTitles:
    """A `NativeSessionTitleRepository` that records rather than writes."""

    def __init__(self, calls: list[tuple[str, str]]) -> None:
        """Keep the title call list and create a rename-check record."""
        self.calls = calls
        self.rename_checks: list[str] = []

    def renameable(self, source_reference: str) -> bool:
        """Record a title-write support check.

        Returns:
            True for every test source.

        """
        self.rename_checks.append(source_reference)
        return True

    def set_title(
        self,
        source_reference: str,
        title: str,
    ) -> TitleWriteOutcome:
        """Record a title write without changing a native file.

        Returns:
            The successful rename outcome.

        """
        self.calls.append((source_reference, title))
        return TitleWriteOutcome.RENAMED
