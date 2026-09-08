# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check browser feed content and history."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import FileOperations


@then(parsers.parse("the browser shows the exact text '{text}'"))
def browser_shows_exact_text(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check exact browser text."""
    browser_session_driver.assert_text_visible(text)


@then(parsers.parse("the browser feed shows text containing '{text}'"))
def browser_feed_shows_text_containing(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check text in the browser feed."""
    browser_session_driver.assert_feed_text_containing_visible(text)


@then(parsers.parse("the browser feed does not show text containing '{text}'"))
def browser_feed_does_not_show_text_containing(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check absent text in the browser feed."""
    browser_session_driver.assert_feed_text_containing_absent(text)


@then(parsers.parse('the browser renders added and removed colors for file operation "{operation_name}"'))
def browser_renders_file_diff_colors(
    browser_session_driver: BrowserSessionDriver,
    file_operations: FileOperations,
    operation_name: str,
) -> None:
    """Check file-diff colors in the browser."""
    browser_session_driver.assert_file_diff_colors(file_operations.get(operation_name))


@then(parsers.parse("the browser can load older session activity automatically containing '{text}'"))
def browser_offers_older_session_activity(browser_session_driver: BrowserSessionDriver, text: str) -> None:
    """Check that the browser can load older activity."""
    browser_session_driver.assert_older_history_available(text)


@when("I scroll to older session activity in the browser")
def load_older_session_activity(browser_session_driver: BrowserSessionDriver) -> None:
    """Load older browser activity."""
    browser_session_driver.load_older_history()
