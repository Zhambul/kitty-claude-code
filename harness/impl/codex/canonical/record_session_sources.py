# Copyright (c) 2026 Zhambyl Yermagambet
"""Own session sources models."""

from __future__ import annotations

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_config import FOREIGN
from harness.impl.codex.ids_session_types import CodexSessionId
from harness.impl.codex.model import BaseInstructionsSourceType, CodexModel


class ThreadSpawn(BaseModel):
    """Represent thread spawn."""

    model_config = FOREIGN
    parent_thread_id: CodexSessionId | None = None
    agent_path: str | None = None
    depth: int | None = None
    agent_nickname: str | None = None
    agent_role: str | None = None


class SubagentSource(BaseModel):
    """Represent subagent source."""

    model_config = FOREIGN
    thread_spawn: ThreadSpawn | None = None


class SessionMetaSource(BaseModel):
    """Represent session meta source."""

    model_config = FOREIGN
    subagent: SubagentSource | None = None


class SessionMetaBaseInstructionsSource(BaseModel):
    """Represent session meta base instructions source."""

    model_config = FOREIGN
    type: BaseInstructionsSourceType
    model: CodexModel


class SessionMetaBaseInstructions(BaseModel):
    """Represent session meta base instructions."""

    model_config = FOREIGN
    text: str | None = None
    source: SessionMetaBaseInstructionsSource | None = Field(
        default=None,
        validation_alias="provenance",
    )


class SessionMetaContextWindow(BaseModel):
    """Represent session meta context window."""

    model_config = FOREIGN
    window_id: str | None = None


class SessionMetaHistoryBase(BaseModel):
    """The immutable rollout prefix used by a paginated rewind."""

    model_config = FOREIGN
    thread_id: CodexSessionId
    end_ordinal_exclusive: int
    end_byte_offset: int
