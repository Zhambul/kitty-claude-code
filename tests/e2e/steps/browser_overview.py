# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that open the browser session overview."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import given, parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.browser import BrowserSessionDriver


@given("the browser is on the session list")
def browser_is_on_session_list(browser_session_driver: BrowserSessionDriver) -> None:
    """Open the browser session list."""
    browser_session_driver.open_session_list()


@given(parsers.parse("the next browser application read omits usage for {harness}"))
def next_browser_application_read_omits_usage(browser_session_driver: BrowserSessionDriver, harness: str) -> None:
    """Omit one harness usage row from the next application read."""
    browser_session_driver.omit_usage_from_next_application_read(harness)


@when("I open the browser session list")
def open_browser_session_list(browser_session_driver: BrowserSessionDriver) -> None:
    """Open the browser session list."""
    browser_session_driver.open_session_list()


@then(parsers.parse("the browser shows the {harness} usage row without reloading the document"))
def browser_shows_usage_without_reload(browser_session_driver: BrowserSessionDriver, harness: str) -> None:
    """Check that a usage row appears without a document reload."""
    browser_session_driver.assert_usage_row_appears_without_reload(harness)
