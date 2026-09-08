# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that control and check browser prompt queues."""

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
    from tests.e2e.testkit.references import Sessions


@when("I reload the browser session list")
def reload_browser_session_list(browser_session_driver: BrowserSessionDriver) -> None:
    """Reload the browser session list."""
    browser_session_driver.reload_session_list()


@when("I stop the current turn in the browser")
def stop_current_turn_in_browser(browser_session_driver: BrowserSessionDriver) -> None:
    """Stop the current browser turn."""
    browser_session_driver.interrupt_turn()


@then(parsers.parse("the browser shows queued prompt '{text}'"))
def browser_shows_queued_prompt(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check that the browser shows a queued prompt."""
    browser_session_driver.assert_queued_prompt(text)


@then(parsers.parse("the browser does not show queued prompt '{text}'"))
def browser_does_not_show_queued_prompt(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check that the browser does not show a queued prompt."""
    browser_session_driver.assert_no_queued_prompt(text)


@then(parsers.parse("session \"{session_name}\" has queued prompt '{text}' after a fresh application read"))
def session_has_queued_prompt_after_fresh_read(
    client: BaqylauClient,
    sessions: Sessions,
    wait_policy: WaitPolicy,
    session_name: str,
    text: str,
) -> None:
    """Wait for a queued prompt in a fresh application read."""
    session = sessions.get(session_name)
    wait_for(
        f"session {session_name!r} to keep queued prompt {text!r}",
        partial(composer_states.queue_has_text, client, session, text),
        timeout=wait_policy.feed,
    )
