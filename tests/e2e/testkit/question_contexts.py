# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for question steps."""

from __future__ import annotations

from dataclasses import dataclass

from sdk.client import BaqylauClient
from tests.e2e.testkit import references as refs
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.questions import QuestionWorkDriver


@dataclass(frozen=True)
class QuestionWorkContext:
    """Contain services for question work."""

    driver: QuestionWorkDriver
    session_specs: refs.SessionSpecs
    sessions: refs.Sessions
    turns: refs.Turns
    works: refs.Works


@dataclass(frozen=True)
class QuestionObservationContext:
    """Contain services for question observations."""

    client: BaqylauClient
    turns: refs.Turns
    questions: refs.Questions
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class QuestionInteractionContext:
    """Contain services for question interactions."""

    client: BaqylauClient
    questions: refs.Questions
    controls: refs.Controls
    turns: refs.Turns
    wait_policy: WaitPolicy
