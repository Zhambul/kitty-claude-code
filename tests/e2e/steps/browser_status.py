# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check browser session status and attention."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

if TYPE_CHECKING:
    from tests.e2e.testkit import browser as browser_testkit, references as refs


@then(parsers.parse('the browser session card for "{session_name}" has status {status} and its canonical color'))
def browser_session_card_has_status(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    sessions: refs.Sessions,
    session_name: str,
    status: str,
) -> None:
    """Check the status and color of one session card."""
    browser_session_driver.assert_session_card_status(sessions.get(session_name), status)


@then(parsers.parse("the browser session header has status {status} and its canonical color"))
def browser_session_header_has_status(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    status: str,
) -> None:
    """Check the status and color of the current session header."""
    browser_session_driver.assert_session_header_status(status)


@then(parsers.parse("the browser session header has title '{title}'"))
def browser_session_header_has_title(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    title: str,
) -> None:
    """Check the title of the current session header."""
    browser_session_driver.assert_session_header_title(title)


@then(parsers.parse('the browser attention badge for "{session_name}" has status {status} and its canonical color'))
def browser_attention_badge_has_status(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    sessions: refs.Sessions,
    session_name: str,
    status: str,
) -> None:
    """Check the status and color of one attention badge."""
    browser_session_driver.assert_attention_status(sessions.get(session_name), status)


@then(parsers.parse("the browser has {count:d} asking session badges"))
def browser_has_asking_session_badges(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    count: int,
) -> None:
    """Check the number of asking session badges."""
    browser_session_driver.assert_asking_count(count)
