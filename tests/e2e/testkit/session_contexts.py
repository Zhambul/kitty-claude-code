# Copyright (c) 2026 Zhambyl Yermagambet
"""Contain focused dependencies for session BDD steps."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from sdk.client import BaqylauClient
from tests.e2e.testkit.policy import WaitPolicy
from tests.e2e.testkit.references import (
    Controls,
    SessionContinuations,
    Sessions,
    SessionSpecs,
    Turns,
)
from tests.e2e.testkit.repository import RepositoryWorkspace


@dataclass(frozen=True)
class SessionConfigContext:
    """Contain common session configuration services."""

    session_specs: SessionSpecs
    pytestconfig: pytest.Config


@dataclass(frozen=True)
class WorkspaceSessionConfigContext:
    """Contain session configuration services and a workspace."""

    common: SessionConfigContext
    workspace: str


@dataclass(frozen=True)
class RepositorySessionConfigContext:
    """Contain session configuration services and a repository workspace."""

    common: SessionConfigContext
    repository: RepositoryWorkspace


@dataclass(frozen=True)
class SessionPromptContext:
    """Contain services for prompt delivery."""

    client: BaqylauClient
    sessions: Sessions
    turns: Turns


@dataclass(frozen=True)
class PromptRequest:
    """Describe one named prompt delivery."""

    session_name: str
    turn_name: str
    prompt: str


@dataclass(frozen=True)
class SessionControlContext:
    """Contain prompt delivery services and control references."""

    prompts: SessionPromptContext
    controls: Controls
    wait_policy: WaitPolicy


@dataclass(frozen=True)
class SessionContinuationContext:
    """Contain services for a continued session."""

    prompts: SessionPromptContext
    continuations: SessionContinuations
    wait_policy: WaitPolicy
