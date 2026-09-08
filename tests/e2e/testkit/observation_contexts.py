# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for work observation steps."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.terminal_models import PaneGeometry
from tests.e2e.testkit.terminals import RealTerminalDriver


@dataclass(frozen=True)
class WorkObservationContext[ReferenceT]:
    """Contain services and references for one work observation type."""

    client: BaqylauClient
    works: refs.Works
    references: refs.References[ReferenceT]
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class TerminalGeometryContext:
    """Contain services for terminal geometry observations."""

    driver: RealTerminalDriver
    geometries: refs.References[PaneGeometry]
    journeys: refs.SessionJourneys


@dataclass(frozen=True)
class CompactionObservationContext:
    """Contain services for compaction observations."""

    client: BaqylauClient
    sessions: refs.Sessions
    controls: refs.Controls
    compactions: refs.Compactions
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class FeedReadContext:
    """Contain services for named feed reads."""

    client: BaqylauClient
    sessions: refs.Sessions
    snapshots: refs.FeedSnapshots


@dataclass(frozen=True)
class GlobalStreamObservationContext:
    """Contain references for global stream observations."""

    updates: refs.GlobalStreamUpdates
    checkpoints: refs.StreamCheckpoints
    sessions: refs.Sessions


@dataclass(frozen=True)
class ResumableSearchContext:
    """Contain services for resumable session searches."""

    client: BaqylauClient
    workspace: str
    resumable_lists: refs.ResumableLists
    sessions: refs.Sessions


@dataclass(frozen=True)
class InsightSessionContext:
    """Contain services for session insight checks."""

    client: BaqylauClient
    snapshots: refs.InsightsSnapshots
    sessions: refs.Sessions
