# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture workspace."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies

REFERENCE_SESSION_NAME = "session"


@fixture_dependencies.application.pytest.fixture
def account_selections() -> fixture_dependencies.drivers.refs.AccountSelections:
    """Create the named references for account selections.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("account selection")


@fixture_dependencies.application.pytest.fixture
def sessions() -> fixture_dependencies.drivers.refs.Sessions:
    """Create the named references for sessions.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References(REFERENCE_SESSION_NAME)


@fixture_dependencies.application.pytest.fixture
def session_continuations() -> fixture_dependencies.drivers.refs.SessionContinuations:
    """Create the named references for session continuations.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("session continuation")


@fixture_dependencies.application.pytest.fixture
def application_restarts() -> fixture_dependencies.drivers.refs.ApplicationRestarts:
    """Create the named references for application restarts.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("application restart")


@fixture_dependencies.application.pytest.fixture
def session_journeys() -> fixture_dependencies.drivers.refs.SessionJourneys:
    """Create the named references for session journeys.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("session journey")


@fixture_dependencies.application.pytest.fixture
def turns() -> fixture_dependencies.drivers.refs.Turns:
    """Create the named references for turns.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("turn")


@fixture_dependencies.application.pytest.fixture
def browser_actions() -> fixture_dependencies.drivers.refs.BrowserActions:
    """Create the named references for browser actions.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("browser action")
