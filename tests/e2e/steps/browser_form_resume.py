# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that resume sessions from browser session forms."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit import browser_contexts
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import BrowserSessionForms, Sessions


@then(parsers.parse('browser session form "{form_name}" requests the resume catalog'))
def browser_session_form_requests_resume_catalog(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
) -> None:
    """Check that a browser session form requested the resume catalog."""
    browser_session_driver.assert_form_requested_resume_catalog(browser_session_forms.get(form_name))


@then(parsers.parse('browser session form "{form_name}" offers session "{session_name}"'))
def browser_session_form_offers_session(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    sessions: Sessions,
    form_name: str,
    session_name: str,
) -> None:
    """Check that a session form offers its source session.

    Raises:
        AssertionError: If the form belongs to a different session.

    """
    form = browser_session_forms.get(form_name)
    if form.source != sessions.get(session_name):
        message = "browser session form belongs to a different session"
        raise AssertionError(message)
    browser_session_driver.assert_form_offers_source(form)


@when(
    parsers.parse(
        'I resume session "{session_name}" from browser session form "{form_name}" as turn "{turn_name}" with prompt',
    ),
)
def resume_from_browser_session_form(
    browser_form_resume_context: browser_contexts.BrowserFormResumeContext,
    session_name: str,
    form_name: str,
    turn_name: str,
    docstring: str,
) -> None:
    """Resume a session from its browser form.

    Raises:
        AssertionError: If the form belongs to a different session.

    """
    form = browser_form_resume_context.forms.get(form_name)
    if form.source != browser_form_resume_context.sessions.get(session_name):
        message = "browser session form belongs to a different session"
        raise AssertionError(message)
    resumed = browser_form_resume_context.driver.resume_from_session_form(form, docstring.strip())
    browser_form_resume_context.sessions.replace(session_name, resumed.session)
    browser_form_resume_context.continuations.bind(session_name, resumed.continuation)
    browser_form_resume_context.turns.bind(turn_name, resumed.turn)
