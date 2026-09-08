# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for browser steps."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.browser import BrowserSessionDriver
from tests.e2e.testkit.policy import WaitPolicy


@dataclass(frozen=True)
class BrowserStartContext:
    """Contain services for a browser session start."""

    driver: BrowserSessionDriver
    session_specs: refs.SessionSpecs
    sessions: refs.Sessions
    turns: refs.Turns


@dataclass(frozen=True)
class BrowserResumeContext:
    """Contain services for a browser session resume."""

    driver: BrowserSessionDriver
    sessions: refs.Sessions
    continuations: refs.SessionContinuations
    turns: refs.Turns


@dataclass(frozen=True)
class BrowserFormResumeContext:
    """Contain services for a browser form resume."""

    driver: BrowserSessionDriver
    forms: refs.BrowserSessionForms
    sessions: refs.Sessions
    continuations: refs.SessionContinuations
    turns: refs.Turns


@dataclass(frozen=True)
class BrowserPromptContext:
    """Contain services for a browser prompt."""

    driver: BrowserSessionDriver
    sessions: refs.Sessions
    turns: refs.Turns


@dataclass(frozen=True)
class BrowserPlanContext:
    """Contain services for a browser plan decision."""

    client: BaqylauClient
    actions: refs.BrowserActions
    plans: refs.Plans
    wait_policy: WaitPolicy
