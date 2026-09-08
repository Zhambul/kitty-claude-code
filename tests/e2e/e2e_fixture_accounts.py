# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture accounts."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def tasks() -> fixture_dependencies.drivers.refs.Tasks:
    """Create the named references for tasks.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("task")


@fixture_dependencies.application.pytest.fixture
def compactions() -> fixture_dependencies.drivers.refs.Compactions:
    """Create the named references for compactions.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("compaction")


@fixture_dependencies.application.pytest.fixture
def harness_lists() -> fixture_dependencies.drivers.refs.HarnessLists:
    """Create the named references for harness lists.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("harness list")


@fixture_dependencies.application.pytest.fixture
def harness_catalogs() -> fixture_dependencies.drivers.refs.HarnessCatalogs:
    """Create the named references for harness catalogs.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("harness catalog")


@fixture_dependencies.application.pytest.fixture
def insights_snapshots() -> fixture_dependencies.drivers.refs.InsightsSnapshots:
    """Create the named references for insights snapshots.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("insights snapshot")


@fixture_dependencies.application.pytest.fixture
def resumable_lists() -> fixture_dependencies.drivers.refs.ResumableLists:
    """Create the named references for resumable lists.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("resumable list")


@fixture_dependencies.application.pytest.fixture
def browser_session_forms() -> fixture_dependencies.drivers.refs.BrowserSessionForms:
    """Create the named references for browser session forms.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("browser session form")
