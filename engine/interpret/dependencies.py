# Copyright (c) 2026 Zhambyl Yermagambet
"""Group interpreter dependencies by responsibility."""

from __future__ import annotations

import dataclasses
import time
from collections.abc import Callable, Mapping

from audit.recorder import AuditRecorder
from harness.contract import (
    CanonicalEventReaction,
    CoreTranslator,
    SessionResumeRecorder,
    SessionTerminalState,
)
from harness.models.interrupts import InterruptRegistry
from harness.registry import HarnessRegistry
from repository.contract.facts import CanonicalEventRepository, RawEventRepository
from repository.contract.sessions import SessionRepository
from repository.contract.shell_output import ShellOutputRepository


@dataclasses.dataclass(frozen=True)
class InterpreterRepositories:
    """Hold interpreter persistence dependencies."""

    sessions: SessionRepository
    raw_events: RawEventRepository
    shell_output: ShellOutputRepository
    canonical_events: CanonicalEventRepository


@dataclasses.dataclass(frozen=True)
class InterpreterServices:
    """Hold interpreter translation and audit services."""

    harnesses: HarnessRegistry
    core_translators: Mapping[str, CoreTranslator]
    inputs: tuple[CanonicalEventReaction, ...]
    audit: AuditRecorder
    interrupts: InterruptRegistry


@dataclasses.dataclass(frozen=True)
class InterpreterRuntime:
    """Hold optional runtime integrations and the wall clock."""

    clock: Callable[[], float] = time.time
    terminal: SessionTerminalState | None = None
    resume_recorder: SessionResumeRecorder | None = None


@dataclasses.dataclass(frozen=True)
class InterpreterDependencies:
    """Compose all interpreter dependencies."""

    repositories: InterpreterRepositories
    services: InterpreterServices
    runtime: InterpreterRuntime = dataclasses.field(default_factory=InterpreterRuntime)
