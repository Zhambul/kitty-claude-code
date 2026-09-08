# Copyright (c) 2026 Zhambyl Yermagambet
"""Own collaboration arguments models."""

from __future__ import annotations

from pydantic import BaseModel

from harness.impl.codex.canonical.record_config import FOREIGN, OPEN_FOREIGN


class SendMessageArguments(BaseModel):
    """Represent send message arguments."""

    model_config = FOREIGN
    message: str | None = None
    content: str | None = None
    target: str | None = None


class SpawnAgentArguments(BaseModel):
    """Represent spawn agent arguments."""

    model_config = OPEN_FOREIGN


class WaitAgentArguments(BaseModel):
    """Represent wait agent arguments."""

    model_config = OPEN_FOREIGN


class InterruptAgentArguments(BaseModel):
    """Represent interrupt agent arguments."""

    model_config = OPEN_FOREIGN


class ListAgentsArguments(BaseModel):
    """Represent list agents arguments."""

    model_config = OPEN_FOREIGN


class FollowupTaskArguments(BaseModel):
    """Represent followup task arguments."""

    model_config = OPEN_FOREIGN
