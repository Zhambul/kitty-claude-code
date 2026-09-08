# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that control browser session alerts."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit import browser as browser_testkit, references as refs


@when(parsers.parse('I mute alerts for session "{session_name}" in the browser'))
def mute_session_alerts_in_browser(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    sessions: refs.Sessions,
    session_name: str,
) -> None:
    """Mute alerts for one session."""
    browser_session_driver.set_session_notifications_muted(sessions.get(session_name), muted=True)


@when(parsers.parse('I enable alerts for session "{session_name}" in the browser'))
def enable_session_alerts_in_browser(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    sessions: refs.Sessions,
    session_name: str,
) -> None:
    """Enable alerts for one session."""
    browser_session_driver.set_session_notifications_muted(sessions.get(session_name), muted=False)


@then(parsers.parse('browser alerts for session "{session_name}" are {state}'))
def browser_session_alerts_are(
    browser_session_driver: browser_testkit.BrowserSessionDriver,
    sessions: refs.Sessions,
    session_name: str,
    state: str,
) -> None:
    """Check the alert state for one session.

    Raises:
        AssertionError: If the state is not valid.

    """
    if state not in {"muted", "enabled"}:
        message = f"unknown browser alert state {state!r}"
        raise AssertionError(message)
    browser_session_driver.assert_session_notifications_muted(
        sessions.get(session_name),
        muted=state == "muted",
    )


@when("I disable global alerts in the browser")
def disable_global_alerts_in_browser(browser_session_driver: browser_testkit.BrowserSessionDriver) -> None:
    """Disable global alerts."""
    browser_session_driver.set_global_notifications(enabled=False)


@when("I enable global alerts in the browser")
def enable_global_alerts_in_browser(browser_session_driver: browser_testkit.BrowserSessionDriver) -> None:
    """Enable global alerts."""
    browser_session_driver.set_global_notifications(enabled=True)


@then(parsers.parse("global browser alerts are {state}"))
def global_browser_alerts_are(browser_session_driver: browser_testkit.BrowserSessionDriver, state: str) -> None:
    """Check the global alert state.

    Raises:
        AssertionError: If the state is not valid.

    """
    if state not in {"enabled", "disabled"}:
        message = f"unknown global browser alert state {state!r}"
        raise AssertionError(message)
    browser_session_driver.assert_global_notifications(enabled=state == "enabled")
