# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check browser resume and account behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

from tests.e2e.testkit import resume

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import BrowserSessionForms, SessionContinuations


@then(parsers.parse('browser resume "{session_name}" keeps its metadata and one live session'))
def browser_resume_keeps_metadata_and_one_live(
    client: BaqylauClient,
    session_continuations: SessionContinuations,
    session_name: str,
) -> None:
    """Check that a browser resume keeps its saved metadata."""
    continuation = session_continuations.get(session_name)
    resume.assert_saved_metadata(client, continuation)
    resume.assert_one_live_session(client, continuation)


@then(parsers.parse("the browser shows the {harness} {model} model usage limit for its default account"))
def browser_shows_model_usage_limit(
    browser_session_driver: BrowserSessionDriver,
    harness: str,
    model: str,
) -> None:
    """Check the default-account model usage limit."""
    browser_session_driver.assert_default_model_usage_window(harness, model)


@then(parsers.parse('browser session form "{form_name}" has no account selection'))
def browser_session_form_has_no_account_selection(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
) -> None:
    """Check that a session form has no account selection."""
    browser_session_driver.assert_session_form_has_no_account_selection(browser_session_forms.get(form_name))
