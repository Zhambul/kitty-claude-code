# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture files."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def reasoning_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    works: fixture_dependencies.drivers.refs.Works,
    reasoning_traces: fixture_dependencies.drivers.refs.ReasoningTraces,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.observation_contexts.WorkObservationContext[
    fixture_dependencies.drivers.refs.ReasoningTraceRef
]:
    """Return services for reasoning trace observations.

    Returns:
        Services for reasoning trace observations.

    """
    return fixture_dependencies.drivers.observation_contexts.WorkObservationContext(
        client, works, reasoning_traces, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def worktree_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    works: fixture_dependencies.drivers.refs.Works,
    worktree_changes: fixture_dependencies.drivers.refs.WorktreeChanges,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.observation_contexts.WorkObservationContext[
    fixture_dependencies.drivers.refs.WorktreeChangeRef
]:
    """Return services for worktree change observations.

    Returns:
        Services for worktree change observations.

    """
    return fixture_dependencies.drivers.observation_contexts.WorkObservationContext(
        client, works, worktree_changes, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def compaction_observation_context(
    client: fixture_dependencies.harness.BaqylauClient,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    controls: fixture_dependencies.drivers.refs.Controls,
    compactions: fixture_dependencies.drivers.refs.Compactions,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.observation_contexts.CompactionObservationContext:
    """Return services for compaction observations.

    Returns:
        Services for compaction observations.

    """
    return fixture_dependencies.drivers.observation_contexts.CompactionObservationContext(
        client, sessions, controls, compactions, wait_policy,
    )


@fixture_dependencies.application.pytest.fixture
def feed_read_context(
    client: fixture_dependencies.harness.BaqylauClient,
    sessions: fixture_dependencies.drivers.refs.Sessions,
    feed_snapshots: fixture_dependencies.drivers.refs.FeedSnapshots,
) -> fixture_dependencies.drivers.observation_contexts.FeedReadContext:
    """Return services for named feed reads.

    Returns:
        Services for named feed reads.

    """
    return fixture_dependencies.drivers.observation_contexts.FeedReadContext(client, sessions, feed_snapshots)


@fixture_dependencies.application.pytest.fixture
def resumable_search_context(
    client: fixture_dependencies.harness.BaqylauClient,
    workspace: str,
    resumable_lists: fixture_dependencies.drivers.refs.ResumableLists,
    sessions: fixture_dependencies.drivers.refs.Sessions,
) -> fixture_dependencies.drivers.observation_contexts.ResumableSearchContext:
    """Return services for resumable session searches.

    Returns:
        Services for resumable session searches.

    """
    return fixture_dependencies.drivers.observation_contexts.ResumableSearchContext(
        client, workspace, resumable_lists, sessions,
    )


@fixture_dependencies.application.pytest.fixture
def insight_session_context(
    client: fixture_dependencies.harness.BaqylauClient,
    insights_snapshots: fixture_dependencies.drivers.refs.InsightsSnapshots,
    sessions: fixture_dependencies.drivers.refs.Sessions,
) -> fixture_dependencies.drivers.observation_contexts.InsightSessionContext:
    """Return services for session insight checks.

    Returns:
        Services for session insight checks.

    """
    return fixture_dependencies.drivers.observation_contexts.InsightSessionContext(client, insights_snapshots, sessions)


@fixture_dependencies.application.pytest.fixture
def file_fixture_context(
    client: fixture_dependencies.harness.BaqylauClient,
    turns: fixture_dependencies.drivers.refs.Turns,
    file_operations: fixture_dependencies.drivers.refs.FileOperations,
    file_operation_path: str,
    wait_policy: fixture_dependencies.drivers.WaitPolicy,
) -> fixture_dependencies.drivers.action_contexts.FileFixtureContext:
    """Return services for fixture file observations.

    Returns:
        Services for fixture file observations.

    """
    return fixture_dependencies.drivers.action_contexts.FileFixtureContext(
        client, turns, file_operations, file_operation_path, wait_policy,
    )
