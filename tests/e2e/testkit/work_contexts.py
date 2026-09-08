# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for work steps."""

from __future__ import annotations

from dataclasses import dataclass

from tests.e2e.testkit import references as refs
from tests.e2e.testkit.work import WorkDriver


@dataclass(frozen=True)
class WorkLaunchContext:
    """Contain services for work launches."""

    driver: WorkDriver
    session_specs: refs.SessionSpecs
    sessions: refs.Sessions
    turns: refs.Turns
    works: refs.Works


@dataclass(frozen=True)
class WorkControlContext:
    """Contain services for work controls."""

    driver: WorkDriver
    session_specs: refs.SessionSpecs
    works: refs.Works
    controls: refs.WorkerControls
