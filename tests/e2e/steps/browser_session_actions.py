# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that navigate browser sessions and send prompts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit import browser_contexts
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import Sessions


@then(parsers.parse('the browser shows session "{session_name}"'))
def browser_shows_session(
    browser_session_driver: BrowserSessionDriver,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Check that the browser shows one session."""
    browser_session_driver.assert_showing(sessions.get(session_name))


@when(parsers.parse('I close browser session "{session_name}"'))
def close_browser_session(
    browser_session_driver: BrowserSessionDriver,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Close one browser session."""
    browser_session_driver.close_session(sessions.get(session_name))


@when(parsers.parse('I open session "{session_name}" in the browser'))
def open_session_in_browser(
    browser_session_driver: BrowserSessionDriver,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Open one session in the browser."""
    browser_session_driver.open_session(sessions.get(session_name))


@when(parsers.parse('I send browser prompt to session "{session_name}" as turn "{turn_name}"'))
def send_browser_prompt(
    browser_prompt_context: browser_contexts.BrowserPromptContext,
    session_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Send one browser prompt."""
    browser_prompt_context.turns.bind(
        turn_name,
        browser_prompt_context.driver.send_prompt(
            browser_prompt_context.sessions.get(session_name),
            docstring.strip(),
        ),
    )
