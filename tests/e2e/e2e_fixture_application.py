# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture application."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def actors() -> fixture_dependencies.drivers.refs.Actors:
    """Create the named references for actors.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("actor")


@fixture_dependencies.application.pytest.fixture
def actor_messages() -> fixture_dependencies.drivers.refs.ActorMessages:
    """Create the named references for actor messages.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("actor message")


@fixture_dependencies.application.pytest.fixture
def assignments() -> fixture_dependencies.drivers.refs.Assignments:
    """Create the named references for assignments.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("assignment")


@fixture_dependencies.application.pytest.fixture
def file_operations() -> fixture_dependencies.drivers.refs.FileOperations:
    """Create the named references for file operations.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("file operation")


@fixture_dependencies.application.pytest.fixture
def searches() -> fixture_dependencies.drivers.refs.Searches:
    """Create the named references for searches.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("web search")


@fixture_dependencies.application.pytest.fixture
def web_fetches() -> fixture_dependencies.drivers.refs.WebFetches:
    """Create the named references for web fetches.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("web fetch")


@fixture_dependencies.application.pytest.fixture
def reasoning_traces() -> fixture_dependencies.drivers.refs.ReasoningTraces:
    """Create the named references for reasoning traces.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("reasoning trace")
