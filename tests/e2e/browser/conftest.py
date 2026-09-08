# Copyright (c) 2026 Zhambyl Yermagambet
"""A real Chrome page for browser-origin Gherkin cases."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.e2e.testkit import browser_contexts
from tests.e2e.testkit.browser import BrowserSessionDriver

if TYPE_CHECKING:
    from collections.abc import Iterator

    from playwright.sync_api import Page

    from sdk.client import BaqylauClient
    from tests.e2e.testkit import references as refs
    from tests.e2e.testkit.policy import WaitPolicy
    from tests.e2e.testkit.process import ApplicationProcess


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, object],
) -> dict[str, object]:
    """Select Chrome for the browser tests.

    Returns:
        The supplied launch options with the channel set to Chrome.

    """
    return {**browser_type_launch_args, "channel": "chrome"}


@pytest.fixture
def browser_session_driver(
    page: Page,
    client: BaqylauClient,
    application_process: ApplicationProcess,
    workspace: str,
    wait_policy: WaitPolicy,
) -> Iterator[BrowserSessionDriver]:
    """Build a browser driver and check it for errors after the test.

    Yields:
        The browser session driver for the test application.

    """
    driver = BrowserSessionDriver(
        page,
        client,
        application_process.endpoint.url,
        workspace,
        wait_policy,
    )
    yield driver
    driver.assert_clean()


@pytest.fixture
def browser_start_context(
    browser_session_driver: BrowserSessionDriver,
    session_specs: refs.SessionSpecs,
    sessions: refs.Sessions,
    turns: refs.Turns,
) -> browser_contexts.BrowserStartContext:
    """Return services for a browser session start.

    Returns:
        Services for a browser session start.

    """
    return browser_contexts.BrowserStartContext(
        browser_session_driver,
        session_specs,
        sessions,
        turns,
    )


@pytest.fixture
def browser_resume_context(
    browser_session_driver: BrowserSessionDriver,
    sessions: refs.Sessions,
    session_continuations: refs.SessionContinuations,
    turns: refs.Turns,
) -> browser_contexts.BrowserResumeContext:
    """Return services for a browser session resume.

    Returns:
        Services for a browser session resume.

    """
    return browser_contexts.BrowserResumeContext(
        browser_session_driver,
        sessions,
        session_continuations,
        turns,
    )


@pytest.fixture
def browser_form_resume_context(
    browser_session_driver: BrowserSessionDriver,
    browser_session_forms: refs.BrowserSessionForms,
    sessions: refs.Sessions,
    session_continuations: refs.SessionContinuations,
    turns: refs.Turns,
) -> browser_contexts.BrowserFormResumeContext:
    """Return services for a browser form resume.

    Returns:
        Services for a browser form resume.

    """
    return browser_contexts.BrowserFormResumeContext(
        browser_session_driver,
        browser_session_forms,
        sessions,
        session_continuations,
        turns,
    )


@pytest.fixture
def browser_prompt_context(
    browser_session_driver: BrowserSessionDriver,
    sessions: refs.Sessions,
    turns: refs.Turns,
) -> browser_contexts.BrowserPromptContext:
    """Return services for a browser prompt.

    Returns:
        Services for a browser prompt.

    """
    return browser_contexts.BrowserPromptContext(
        browser_session_driver,
        sessions,
        turns,
    )


@pytest.fixture
def browser_plan_context(
    client: BaqylauClient,
    browser_actions: refs.BrowserActions,
    plans: refs.Plans,
    wait_policy: WaitPolicy,
) -> browser_contexts.BrowserPlanContext:
    """Return services for a browser plan decision.

    Returns:
        Services for a browser plan decision.

    """
    return browser_contexts.BrowserPlanContext(
        client,
        browser_actions,
        plans,
        wait_policy,
    )
