# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture harness config."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def works() -> fixture_dependencies.drivers.refs.Works:
    """Create the named references for works.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("work")


@fixture_dependencies.application.pytest.fixture
def worker_controls() -> fixture_dependencies.drivers.refs.WorkerControls:
    """Create the named references for worker controls.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("worker control")


@fixture_dependencies.application.pytest.fixture
def feed_snapshots() -> fixture_dependencies.drivers.refs.FeedSnapshots:
    """Create the named references for feed snapshots.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("feed snapshot")


@fixture_dependencies.application.pytest.fixture
def stream_checkpoints() -> fixture_dependencies.drivers.refs.StreamCheckpoints:
    """Create the named references for stream checkpoints.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("stream checkpoint")


@fixture_dependencies.application.pytest.fixture
def session_stream_updates() -> fixture_dependencies.drivers.refs.SessionStreamUpdates:
    """Create the named references for session stream updates.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("session stream update")


@fixture_dependencies.application.pytest.fixture
def global_stream_updates() -> fixture_dependencies.drivers.refs.GlobalStreamUpdates:
    """Create the named references for global stream updates.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("global stream update")


@fixture_dependencies.application.pytest.fixture
def shells() -> fixture_dependencies.drivers.refs.Shells:
    """Create the named references for shells.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("shell command")
