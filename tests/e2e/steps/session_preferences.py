# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that save and check session display preferences."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.references import Sessions


@when(parsers.parse('I set view mode {view_mode} for session "{name}"'))
def set_view_mode(client: BaqylauClient, sessions: Sessions, name: str, view_mode: str) -> None:
    """Set one session view mode."""
    client.preferences.set_view_mode(sessions.get(name), view_mode)


@when(parsers.parse('I mute notifications for session "{name}"'))
def mute_notifications(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Mute notifications for one session."""
    client.preferences.set_notifications_muted(sessions.get(name), muted=True)


@when(parsers.parse('I hide tasks for session "{name}"'))
def hide_tasks(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Hide tasks for one session."""
    client.preferences.set_tasks_hidden(sessions.get(name), hidden=True)


@then(parsers.parse('view mode for session "{name}" is {view_mode}'))
def view_mode_is_saved(client: BaqylauClient, sessions: Sessions, name: str, view_mode: str) -> None:
    """Verify a session view mode."""
    found = client.preferences.session_state(sessions.get(name)).preferences.view_mode
    assert found == view_mode


@then(parsers.parse('notifications for session "{name}" are muted'))
def notifications_are_muted(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Verify session notifications are muted."""
    assert client.preferences.session_state(sessions.get(name)).preferences.notifications_muted


@then(parsers.parse('tasks for session "{name}" are hidden'))
def tasks_are_hidden(client: BaqylauClient, sessions: Sessions, name: str) -> None:
    """Verify session tasks are hidden."""
    assert client.preferences.session_state(sessions.get(name)).preferences.tasks_hidden
