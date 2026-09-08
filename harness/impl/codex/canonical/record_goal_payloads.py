# Copyright (c) 2026 Zhambyl Yermagambet
"""Own goal payloads models."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import FOREIGN, OPEN_FOREIGN
from harness.impl.codex.ids_session_types import CodexSessionId


class GoalBlock(BaseModel):
    """Represent goal block."""

    model_config = FOREIGN
    objective: str | None = None
    status: str | None = None
    reason: str | None = None
    thread_id: Annotated[CodexSessionId | None, Field(alias="threadId")] = None
    tokens_used: Annotated[int | None, Field(alias="tokensUsed")] = None
    time_used_seconds: Annotated[int | None, Field(alias="timeUsedSeconds")] = None
    created_at: Annotated[int | None, Field(alias="createdAt")] = None
    updated_at: Annotated[int | None, Field(alias="updatedAt")] = None


class ThreadGoalUpdatedPayload(BaseModel):
    """Represent thread goal updated payload."""

    model_config = FOREIGN
    type: Literal["thread_goal_updated"] = "thread_goal_updated"
    goal: GoalBlock | None = None
    thread_id: Annotated[CodexSessionId | None, Field(alias="threadId")] = None


class EmptyPayload(BaseModel):
    """Represent empty payload.

    A payload whose handler reads nothing from it: `thread_goal_cleared`,
        `context_compacted`. Declared (rather than skipped) so an unexpected
        field on one of these still fails fast instead of silently riding along
        unread. Shared by both `type` strings, so `type` itself is read but not
        constrained to one of them here — the dispatch table that chose this
        model already did that check.
    """

    model_config = FOREIGN
    type: Literal["thread_goal_cleared", "context_compacted"]


class WorldStatePayload(BaseModel):
    """Represent world state payload.

    A `world_state` top-level record: a large periodic state snapshot
        (open files, shell sessions, todos) — GENUINELY open (module header,
        OPEN_FOREIGN), not a shape this codebase has ever read one field of, let
        alone declared exhaustively.
    """

    model_config = OPEN_FOREIGN


class InterAgentCommunicationMetadataPayload(BaseModel):
    """A v2 child-turn trigger with no user-visible content."""

    model_config = FOREIGN
    trigger_turn: bool
