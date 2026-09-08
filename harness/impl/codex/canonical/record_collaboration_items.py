# Copyright (c) 2026 Zhambyl Yermagambet
"""Own collaboration items models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal

from pydantic import BaseModel, RootModel

from harness.impl.codex.canonical.record_config import FOREIGN
from harness.impl.codex.ids_session_types import CodexActorId


class SubAgentActivityItem(BaseModel):
    """Represent sub agent activity item."""

    model_config = FOREIGN
    type: Literal["SubAgentActivity"]
    kind: str | None = None
    agent_thread_id: CodexActorId | None = None
    agent_path: str | None = None
    id: str | None = None


class CollabAgentReference(BaseModel):
    """Represent collab agent reference."""

    model_config = FOREIGN
    thread_id: CodexActorId
    agent_nickname: str | None = None


class CollabAgentStates(RootModel[Mapping[CodexActorId, str]]):
    """Represent collab agent states."""


class CollabAgentToolCallItem(BaseModel):
    """A collaboration mirror whose child rollout owns the canonical facts."""

    model_config = FOREIGN
    type: Literal["CollabAgentToolCall"]
    id: str | None = None
    tool: str | None = None
    status: str | None = None
    sender_thread_id: CodexActorId | None = None
    receiver_thread_ids: list[CodexActorId] | None = None
    receiver_agents: list[CollabAgentReference] | None = None
    prompt: str | None = None
    model: str | None = None
    reasoning_effort: str | None = None
    agents_states: CollabAgentStates | None = None


class PlanItem(BaseModel):
    """Represent plan item."""

    model_config = FOREIGN
    type: Literal["Plan"]
    text: str | None = None
    id: str | None = None
