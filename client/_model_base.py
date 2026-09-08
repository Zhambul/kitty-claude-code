# Copyright (c) 2026 Zhambyl Yermagambet
"""Model base."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class WireModel(BaseModel):
    # A pane can outlive a daemon upgrade. It validates every field it reads and
    # ignores new response fields that this client version does not use.
    model_config = ConfigDict(extra="ignore")


class ContentRecord(WireModel):
    text: str = ""
    media_type: str = "text/plain"


class AccountRecord(WireModel):
    account_id: str = ""
    display_name: str = ""


class TaskRecord(WireModel):
    task_id: str = ""
    subject: str = ""
    description: str | None = None
    state: str = ""
    owner_actor_id: str | None = None


class GoalRecord(WireModel):
    objective: str | None = None
    state: str = ""
    reason: str | None = None
    completed: bool = False


class SessionRecord(WireModel):
    session_id: str = ""
    harness: str = ""
    title: str | None = None
    state: str = ""
    working_directory: str = ""
    started_at: float | None = None
    finished_at: float | None = None
    account: AccountRecord | None = None
    lead_actor_id: str = ""
    goal: GoalRecord | None = None
    tasks: tuple[TaskRecord, ...] = ()
    continued_from: str | None = None


class TokenRecord(WireModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    one_hour_cache_write_tokens: int = 0
