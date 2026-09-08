# Copyright (c) 2026 Zhambyl Yermagambet
"""Terminal drafts use the same durable composer state as the web page."""

from __future__ import annotations

from types import SimpleNamespace

from domain import (
    composer,
    ids as domain_ids,
)
from harness.models.probe import TerminalSessionState
from tests import terminal_draft_support
from tests.terminal_draft_service import service

BROWSER_EDIT_TIME = 2_000
TERMINAL_EDIT_TIME = 3_000
TEST_SESSION_ID = domain_ids.SessionId("session-one")
WEB_EDIT_TEXT = "web edit"
BROWSER_ORIGIN = "browser-one"


def test_unchanged_terminal_draft_does_not() -> None:
    """Verify an unchanged terminal draft does not overwrite a web edit."""
    states = terminal_draft_support.TerminalStates("test")
    workspaces = terminal_draft_support.Workspaces()
    application = service(states, workspaces, [1.0, 3.0])

    assert application.snapshot(TEST_SESSION_ID).composer.draft == composer.ComposerDraft("test", "terminal", 1000)

    workspaces.save_composer_draft(
        TEST_SESSION_ID,
        composer.ComposerDraft(WEB_EDIT_TEXT, BROWSER_ORIGIN, BROWSER_EDIT_TIME),
    )
    assert application.snapshot(TEST_SESSION_ID).composer.draft == composer.ComposerDraft(
        WEB_EDIT_TEXT,
        BROWSER_ORIGIN,
        BROWSER_EDIT_TIME,
    )

    states.text = "terminal edit"
    assert application.snapshot(TEST_SESSION_ID).composer.draft == composer.ComposerDraft(
        "terminal edit",
        "terminal",
        TERMINAL_EDIT_TIME,
    )


def test_empty_terminal_clears_only_terminal() -> None:
    """Verify an empty terminal clears only a terminal owned draft."""
    session_id = TEST_SESSION_ID
    states = terminal_draft_support.TerminalStates("test")
    workspaces = terminal_draft_support.Workspaces()
    application = service(states, workspaces, [1.0, 2.0])

    application.snapshot(session_id)
    states.text = ""
    assert application.snapshot(session_id).composer.draft is None

    workspaces.save_composer_draft(
        session_id,
        composer.ComposerDraft(WEB_EDIT_TEXT, BROWSER_ORIGIN, TERMINAL_EDIT_TIME),
    )
    assert application.snapshot(session_id).composer.draft == composer.ComposerDraft(
        "web edit",
        BROWSER_ORIGIN,
        TERMINAL_EDIT_TIME,
    )


def test_native_attention_text_is_not_composer() -> None:
    """Verify native attention text is not a composer draft."""
    session_id = domain_ids.SessionId("session-one")
    states = terminal_draft_support.TerminalStates("Which option should I use?")
    workspaces = terminal_draft_support.Workspaces()
    read_model = terminal_draft_support.ReadModel()
    read_model.attention = (SimpleNamespace(body=object()),)

    snapshot = service(states, workspaces, [], read_model).snapshot(session_id)

    assert snapshot.composer.draft is None
    assert snapshot.terminal == TerminalSessionState(domain_ids.WindowId("window-one"), None)


def test_native_attention_does_not_replace_saved() -> None:
    """Verify native attention does not replace a saved browser draft."""
    session_id = domain_ids.SessionId("session-one")
    states = terminal_draft_support.TerminalStates("Approve this plan?")
    workspaces = terminal_draft_support.Workspaces()
    workspaces.save_composer_draft(
        session_id,
        composer.ComposerDraft("browser draft", BROWSER_ORIGIN, 1000),
    )
    read_model = terminal_draft_support.ReadModel()
    read_model.attention = (SimpleNamespace(body=object()),)

    snapshot = service(states, workspaces, [], read_model).snapshot(session_id)

    assert snapshot.composer.draft == composer.ComposerDraft(
        "browser draft",
        BROWSER_ORIGIN,
        1000,
    )
    assert snapshot.terminal == TerminalSessionState(domain_ids.WindowId("window-one"), None)
