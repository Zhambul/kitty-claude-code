# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for planning steps."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.planning import PlanWorkDriver
from tests.e2e.testkit.policy import WaitPolicy


@dataclass(frozen=True)
class PlanWorkContext:
    """Contain services for plan work."""

    driver: PlanWorkDriver
    session_specs: refs.SessionSpecs
    sessions: refs.Sessions
    turns: refs.Turns


@dataclass(frozen=True)
class PlanObservationContext:
    """Contain services for plan observations."""

    client: BaqylauClient
    turns: refs.Turns
    plans: refs.Plans
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class PlanInteractionContext:
    """Contain services for plan interactions."""

    client: BaqylauClient
    plans: refs.Plans
    controls: refs.Controls
    turns: refs.Turns
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class TaskNamingContext:
    """Contain services for task naming."""

    client: BaqylauClient
    sessions: refs.Sessions
    tasks: refs.Tasks
    wait_policy: WaitPolicy
