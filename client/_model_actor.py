# Copyright (c) 2026 Zhambyl Yermagambet
"""Model actor."""

from __future__ import annotations

from _model_base import TokenRecord, WireModel


class UsageRecord(WireModel):
    tokens: TokenRecord = TokenRecord()
    cost_in_usd: str | None = None


class ToolCountRecord(WireModel):
    tool: str
    count: int


class StatisticsRecord(WireModel):
    prompt_count: int = 0
    shell_command_count: int = 0
    failed_shell_command_count: int = 0
    file_count: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    actor_message_count: int = 0
    tool_counts: tuple[ToolCountRecord, ...] = ()
    active_seconds: float = 0
    active: bool = False


class BackgroundRecord(WireModel):
    running_shell_ids: tuple[str, ...] = ()
    monitor_count: int = 0
    background_job_count: int = 0


class ContextRecord(WireModel):
    used_tokens: int = 0
    window_tokens: int = 0
    compacting: bool = False


class ActorRecord(WireModel):
    session_id: str = ""
    actor_id: str
    parent_actor_id: str | None = None
    role: str = ""
    name: str = ""
    description: str | None = None
    state: str = ""
    started_at: float | None = None
    finished_at: float | None = None
    model: str | None = None
    effort: str | None = None
    status: str | None = None
    background: BackgroundRecord = BackgroundRecord()
    statistics: StatisticsRecord = StatisticsRecord()
    usage: UsageRecord = UsageRecord()
    context: ContextRecord = ContextRecord()
