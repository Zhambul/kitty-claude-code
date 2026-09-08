# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that edit and check the browser composer."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from sdk.client import wait_for
from tests.e2e.testkit import composer_states

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.references import Sessions, Turns


@when(parsers.parse("I type composer draft '{text}' in the browser"))
def type_browser_composer_draft(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Type one composer draft."""
    browser_session_driver.type_composer_draft(text)


@then(parsers.parse("the browser composer contains exact draft '{text}'"))
def browser_composer_contains_draft(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check the browser composer draft."""
    browser_session_driver.assert_composer_draft(text)


@then("the browser composer is empty")
def browser_composer_is_empty(browser_session_driver: BrowserSessionDriver) -> None:
    """Check that the browser composer is empty."""
    browser_session_driver.assert_composer_draft("")


@when(parsers.parse('I send the browser composer for session "{session_name}" as turn "{turn_name}"'))
def send_browser_composer_draft(
    browser_session_driver: BrowserSessionDriver,
    sessions: Sessions,
    turns: Turns,
    session_name: str,
    turn_name: str,
) -> None:
    """Send the browser composer draft."""
    turns.bind(turn_name, browser_session_driver.send_composer_draft(sessions.get(session_name)))


@then(parsers.parse("session \"{session_name}\" has composer draft '{text}' after a fresh application read"))
def session_has_composer_draft_after_fresh_read(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    session_name: str,
    text: str,
) -> None:
    """Wait for a saved composer draft."""
    session = sessions.get(session_name)
    wait_for(
        f"session {session_name!r} composer draft to be saved",
        partial(composer_states.draft_is_saved, client, session, text),
        timeout=wait_policy.feed,
    )


@then(parsers.parse('session "{session_name}" has no composer draft after a fresh application read'))
def session_has_no_composer_draft_after_fresh(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    session_name: str,
) -> None:
    """Wait for a cleared composer draft."""
    session = sessions.get(session_name)
    wait_for(
        f"session {session_name!r} composer draft to clear",
        partial(composer_states.draft_is_cleared, client, session),
        timeout=wait_policy.feed,
    )
