# Copyright (c) 2026 Zhambyl Yermagambet
"""Stored state for one actor in a coding session."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum

from domain.ids import ActorId, AssignmentId, AttentionId, SessionId, ShellId
from domain.lifecycle import LifecycleState
from domain.messaging import ActorRole
from domain.references import ModelReference
from domain.stored import STORED
from domain.usage import TokenUsage


class ActorStatus(StrEnum):
    """Show the current activity that a person sees for an actor."""

    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    EXECUTING = "executing"
    AWAITING_BACKGROUND = "awaiting_background"
    AWAITING_ATTENTION = "awaiting_attention"
    AWAITING_RESPONSE = "awaiting_response"


@dataclass(frozen=True)
class ActorUsage:
    """Hold the tokens and cost that one actor used."""

    __pydantic_config__ = STORED

    tokens: TokenUsage = field(default_factory=TokenUsage)
    cost_in_usd: Decimal | None = None


@dataclass(frozen=True)
class ActorContext:
    """Hold the current context-window state for one actor."""

    __pydantic_config__ = STORED

    used_tokens: int = 0
    window_tokens: int = 0
    compacting: bool = False


@dataclass(frozen=True)
class ActorBackground:
    """Hold work that continues after an actor turn ends."""

    __pydantic_config__ = STORED

    running_shell_ids: tuple[ShellId, ...] = ()
    monitor_count: int = 0
    background_job_count: int = 0


@dataclass(frozen=True)
class ToolCount:
    """Hold the number of calls to one tool."""

    __pydantic_config__ = STORED

    tool: str
    count: int


@dataclass(frozen=True)
class ActorStatistics:
    """Hold cumulative work statistics for one actor."""

    __pydantic_config__ = STORED

    prompt_count: int = 0
    shell_command_count: int = 0
    failed_shell_command_count: int = 0
    file_count: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    actor_message_count: int = 0
    tool_counts: tuple[ToolCount, ...] = ()
    active_seconds: float = field(default_factory=float)
    active_since_internal: float | None = None
    file_paths_internal: tuple[str, ...] = ()


@dataclass(frozen=True)
class ActorFacts:
    """Hold the stored aggregate for one actor."""

    __pydantic_config__ = STORED

    session_id: SessionId
    actor_id: ActorId
    role: ActorRole
    name: str
    state: LifecycleState
    parent_actor_id: ActorId | None = None
    description: str | None = None
    started_at: float | None = None
    finished_at: float | None = None
    model: ModelReference | None = None
    effort: str | None = None
    status: ActorStatus | None = None
    usage: ActorUsage = field(default_factory=ActorUsage)
    context: ActorContext = field(default_factory=ActorContext)
    background: ActorBackground = field(default_factory=ActorBackground)
    statistics: ActorStatistics = field(default_factory=ActorStatistics)
    pending_attention_internal: tuple[AttentionId, ...] = ()
    running_assignment_ids_internal: tuple[AssignmentId, ...] = ()
