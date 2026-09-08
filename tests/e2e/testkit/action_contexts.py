# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for file and skill steps."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import (
    FileOperations,
    References,
    Sessions,
    SessionSpecs,
    Shells,
    Skills,
    Turns,
    Works,
)
from tests.e2e.testkit.skill_fixtures import SkillWorkDriver


@dataclass(frozen=True)
class FileFixtureContext:
    """Contain services for fixture file observations."""

    client: BaqylauClient
    turns: Turns
    operations: FileOperations
    path: str
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class WorkspaceFileContext:
    """Contain services for workspace file observations."""

    client: BaqylauClient
    workspace: str
    turns: Turns
    operations: FileOperations
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class SkillLaunchContext:
    """Contain services for skill work launches."""

    driver: SkillWorkDriver
    session_specs: SessionSpecs
    sessions: Sessions
    turns: Turns
    works: Works


@dataclass(frozen=True)
class SkillObservationContext:
    """Contain services for skill observations."""

    client: BaqylauClient
    turns: Turns
    skills: Skills
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class TurnObservationContext[ReferenceT]:
    """Contain services for named observations in one turn."""

    client: BaqylauClient
    turns: Turns
    references: References[ReferenceT]
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class ShellObservationContext:
    """Contain services for shell observations."""

    client: BaqylauClient
    turns: Turns
    shells: Shells
    wait_policy: WaitPolicy
