# Copyright (c) 2026 Zhambyl Yermagambet
"""Group dependencies for committed-event reactions."""

from dataclasses import dataclass

from harness.models.interrupts import (
    InterruptRegistry,
)
from harness.registry import HarnessRegistry
from naming.renamer import SessionRenamer
from repository.contract.naming import NamingJobRepository
from repository.contract.sessions import SessionRepository
from repository.contract.workspace import SessionWorkspaceRepository
from terminal.adapter import TerminalAdapter
from terminal.services.panes import PaneWidthService


@dataclass(frozen=True)
class ReactionTerminalResources:
    """Hold terminal and workspace reaction dependencies."""

    session_repository: SessionRepository
    terminal_adapter: TerminalAdapter
    pane_width_service: PaneWidthService
    workspace_repository: SessionWorkspaceRepository


@dataclass(frozen=True)
class ReactionControlResources:
    """Hold naming and interrupt reaction dependencies."""

    interrupt_registry: InterruptRegistry
    harness_registry: HarnessRegistry
    naming_job_repository: NamingJobRepository
    session_renamer: SessionRenamer
