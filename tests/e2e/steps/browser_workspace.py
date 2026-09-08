# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check browser workspace and stream connection state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.browser import BrowserSessionDriver


@then("the browser shows the configured workspace group")
def browser_shows_workspace_group(browser_session_driver: BrowserSessionDriver) -> None:
    """Check that the workspace group is visible."""
    browser_session_driver.assert_workspace_visible()


@when("I hide the configured workspace group in the browser")
def hide_workspace_group_in_browser(browser_session_driver: BrowserSessionDriver) -> None:
    """Hide the workspace group."""
    browser_session_driver.hide_workspace()


@then("the browser hides the configured workspace group")
def browser_hides_workspace_group(browser_session_driver: BrowserSessionDriver) -> None:
    """Check that the workspace group is hidden."""
    browser_session_driver.assert_workspace_hidden()


@then("the browser event stream is connected")
def browser_event_stream_is_connected(browser_session_driver: BrowserSessionDriver) -> None:
    """Check that the browser event stream is connected."""
    browser_session_driver.assert_connected()


@when("I mark the current browser document for connection recovery")
def mark_browser_document_for_connection_recovery(browser_session_driver: BrowserSessionDriver) -> None:
    """Mark the document for a connection-recovery check."""
    browser_session_driver.mark_document_for_connection_recovery()


@then("the browser event stream reconnects without a reload")
def browser_event_stream_reconnects(browser_session_driver: BrowserSessionDriver) -> None:
    """Check that the browser event stream reconnects."""
    browser_session_driver.assert_reconnected_without_reload()
