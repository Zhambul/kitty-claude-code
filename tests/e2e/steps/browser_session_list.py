# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check the browser session list."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.browser import BrowserSessionDriver
    from tests.e2e.testkit.references import Sessions
    from tests.e2e.testkit.repository import RepositoryWorkspace


@then(parsers.parse('the browser session list shows session "{session_name}"'))
def browser_session_list_shows_session(
    browser_session_driver: BrowserSessionDriver,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Check that the session list shows one session."""
    browser_session_driver.assert_session_card_visible(sessions.get(session_name))


@then(parsers.parse('the browser session list does not show session "{session_name}"'))
def browser_session_list_does_not_show_session(
    browser_session_driver: BrowserSessionDriver,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Check that the session list does not show one session."""
    browser_session_driver.assert_session_card_absent(sessions.get(session_name))


@then(parsers.parse('a fresh application session list does not contain session "{session_name}"'))
def fresh_app_session_list_excludes_session(
    client: BaqylauClient,
    sessions: Sessions,
    session_name: str,
) -> None:
    """Check that a fresh application read excludes one session."""
    excluded = sessions.get(session_name).session_id
    found = [session_summary.session.session_id for session_summary in client.sessions.list().sessions]
    assert excluded not in found, f"application session list contains {excluded!r}"


@then(parsers.parse('browser sessions "{first_name}" and "{second_name}" share the isolated project group'))
def browser_sessions_share_project_group(
    browser_session_driver: BrowserSessionDriver,
    repository_workspace: RepositoryWorkspace,
    sessions: Sessions,
    first_name: str,
    second_name: str,
) -> None:
    """Check that two sessions share their isolated project group."""
    browser_session_driver.assert_shared_project_group(
        (sessions.get(first_name), sessions.get(second_name)),
        repository_workspace.repository_root,
        repository_workspace.working_directory,
    )
