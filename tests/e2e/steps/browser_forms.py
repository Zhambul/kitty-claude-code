# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that edit fresh browser session forms."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import BrowserSessionForms, Sessions, SessionSpecs


@when(parsers.parse('I open fresh browser session form "{form_name}" for session "{session_name}"'))
def open_fresh_browser_session_form(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    sessions: Sessions,
    form_name: str,
    session_name: str,
) -> None:
    """Open a fresh browser session form."""
    browser_session_forms.bind(form_name, browser_session_driver.open_fresh_session_form(sessions.get(session_name)))


@when(
    parsers.parse(
        'I open configured browser session form "{form_name}" using session configuration "{configuration_name}"',
    ),
)
def open_configured_browser_session_form(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    session_specs: SessionSpecs,
    form_name: str,
    configuration_name: str,
) -> None:
    """Open a fresh browser session form from one configuration."""
    browser_session_forms.bind(
        form_name,
        browser_session_driver.open_configured_fresh_session_form(session_specs.get(configuration_name)),
    )


@when(parsers.parse("I type '{text}' in browser session form \"{form_name}\""))
def type_in_browser_session_form(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
    text: str,
) -> None:
    """Type text in a browser session form."""
    browser_session_driver.type_session_form_prompt(browser_session_forms.get(form_name), text)


@when(parsers.parse('I close browser session form "{form_name}"'))
def close_browser_session_form(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
) -> None:
    """Close one browser session form."""
    browser_session_driver.close_session_form(browser_session_forms.get(form_name))


@then(parsers.parse("browser session form \"{form_name}\" contains exact draft '{text}'"))
def browser_session_form_contains_draft(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
    text: str,
) -> None:
    """Check the exact draft in a browser session form."""
    browser_session_driver.assert_session_form_prompt(browser_session_forms.get(form_name), text)


@when(parsers.parse('I switch browser session form "{form_name}" to resume mode'))
def switch_browser_session_form_to_resume(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
) -> None:
    """Switch one browser session form to resume mode."""
    browser_session_forms.replace(
        form_name,
        browser_session_driver.switch_session_form_to_resume(browser_session_forms.get(form_name)),
    )


@then(parsers.parse('browser session form "{form_name}" has not requested the resume catalog'))
def fresh_browser_session_form_does_not_request(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: BrowserSessionForms,
    form_name: str,
) -> None:
    """Check that a fresh form did not request the resume catalog."""
    browser_session_driver.assert_form_did_not_request_resume_catalog(browser_session_forms.get(form_name))
