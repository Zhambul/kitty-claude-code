# Copyright (c) 2026 Zhambyl Yermagambet
"""API models for one session actor."""

from pydantic import BaseModel

from api.common.models.values.token_usage import TokenUsageResponse
from domain.actor_state import ActorStatus
from domain.lifecycle import LifecycleState
from domain.messaging import ActorRole

type ActorStatusResponse = ActorStatus


class ActorUsageResponse(BaseModel):
    """Report actor token usage and cost."""

    tokens: TokenUsageResponse
    cost_in_usd: str | None


class ActorContextResponse(BaseModel):
    """Report actor context-window use."""

    used_tokens: int
    window_tokens: int
    compacting: bool


class ActorBackgroundResponse(BaseModel):
    """Report running and completed background work."""

    running_shell_ids: tuple[str, ...]
    monitor_count: int
    background_job_count: int


class ToolCountResponse(BaseModel):
    """Report one tool invocation count."""

    tool: str
    count: int


class ActorStatisticsResponse(BaseModel):
    """Report the actor activity scoreboard."""

    prompt_count: int
    shell_command_count: int
    failed_shell_command_count: int
    file_count: int
    lines_added: int
    lines_removed: int
    actor_message_count: int
    tool_counts: tuple[ToolCountResponse, ...]
    active_seconds: float
    active: bool


class ActorResponse(BaseModel):
    """Report one actor in one session."""

    session_id: str
    actor_id: str
    parent_actor_id: str | None
    role: ActorRole
    name: str
    description: str | None
    state: LifecycleState
    started_at: float | None
    finished_at: float | None
    model: str | None
    effort: str | None
    status: ActorStatusResponse | None
    usage: ActorUsageResponse
    context: ActorContextResponse
    background: ActorBackgroundResponse
    statistics: ActorStatisticsResponse
