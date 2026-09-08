# Copyright (c) 2026 Zhambyl Yermagambet
"""Data objects returned and used by E2E session journeys."""

from __future__ import annotations

from dataclasses import dataclass

from harness.runtime import HarnessRuntimeConfigs
from terminal.contract import TerminalPlugin
from terminal.models.tabs import EnvironmentVariable
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import SessionContinuationRef, SessionJourneyRef, TurnRef


@dataclass(frozen=True)
class JourneyTurn:
    """Represent one journey turn."""

    journey: SessionJourneyRef
    turn: TurnRef


@dataclass(frozen=True)
class ResumedJourney:
    """Represent one resumed journey."""

    journey: SessionJourneyRef
    continuation: SessionContinuationRef
    turn: TurnRef


@dataclass(frozen=True)
class JourneyEnvironment:
    """Contain terminal journey services and settings."""

    terminal: TerminalPlugin
    workspace: str
    application_port: int
    wait_policy: WaitPolicy
    harness_runtime_configs: HarnessRuntimeConfigs
    launch_environment: tuple[EnvironmentVariable, ...] = ()
