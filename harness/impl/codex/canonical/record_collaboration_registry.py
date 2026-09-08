# Copyright (c) 2026 Zhambyl Yermagambet
"""Own collaboration registry models."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

from harness.impl.codex.canonical.record_collaboration_arguments import (
    FollowupTaskArguments,
    InterruptAgentArguments,
    ListAgentsArguments,
    SendMessageArguments,
    SpawnAgentArguments,
    WaitAgentArguments,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

type CollaborationArguments = (
    SendMessageArguments
    | SpawnAgentArguments
    | WaitAgentArguments
    | InterruptAgentArguments
    | ListAgentsArguments
    | FollowupTaskArguments
)


class CollaborationCallName(StrEnum):
    """Represent collaboration call name."""

    SPAWN_AGENT = "spawn_agent"
    WAIT_AGENT = "wait_agent"
    SEND_MESSAGE = "send_message"
    FOLLOWUP_TASK = "followup_task"
    INTERRUPT_AGENT = "interrupt_agent"
    LIST_AGENTS = "list_agents"


COLLABORATION_ARGUMENTS: Mapping[CollaborationCallName, type[CollaborationArguments]] = MappingProxyType({
    CollaborationCallName.SPAWN_AGENT: SpawnAgentArguments,
    CollaborationCallName.WAIT_AGENT: WaitAgentArguments,
    CollaborationCallName.SEND_MESSAGE: SendMessageArguments,
    CollaborationCallName.FOLLOWUP_TASK: FollowupTaskArguments,
    CollaborationCallName.INTERRUPT_AGENT: InterruptAgentArguments,
    CollaborationCallName.LIST_AGENTS: ListAgentsArguments,
})
