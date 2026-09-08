# Copyright (c) 2026 Zhambyl Yermagambet
"""Own result documents models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from harness.impl.codex.canonical.record_config import OPEN_FOREIGN
from harness.impl.codex.canonical.record_goal_payloads import InterAgentCommunicationMetadataPayload, WorldStatePayload
from harness.impl.codex.canonical.record_rollout_headers import RolloutDocument
from harness.impl.codex.canonical.record_turn_payloads import CompactedPayload, TurnContextPayload
from harness.impl.codex.ids_session_types import CodexShellId


class TurnContextDocument(RolloutDocument[TurnContextPayload]):
    """Represent turn context document."""

    type: Literal["turn_context"] = "turn_context"


class CompactedDocument(RolloutDocument[CompactedPayload]):
    """Represent compacted document."""

    type: Literal["compacted"] = "compacted"


class WorldStateDocument(RolloutDocument[WorldStatePayload]):
    """Represent world state document."""

    type: Literal["world_state"] = "world_state"


class InterAgentCommunicationMetadataDocument(
    RolloutDocument[InterAgentCommunicationMetadataPayload],
):
    """Represent inter agent communication metadata document."""

    type: Literal["inter_agent_communication_metadata"] = "inter_agent_communication_metadata"


class CombinedCommandResult(BaseModel):
    """Represent combined command result."""

    model_config = OPEN_FOREIGN
    output: str | None = None
    exit_code: int | None = None
    session_id: CodexShellId | int | None = None


class CombinedToolResult(BaseModel):
    """Represent combined tool result.

    The `custom_tool_call_output` wrapper's own JSON body — GENUINELY open
        (module header, OPEN_FOREIGN): it freely combines an apply_patch result
        with a command result depending on what the model called in one exec turn,
        and the exact key set is the vendor wrapper's format, not a shape this
        codebase controls. Declared as far as reality allows: the keys our own
        logic reads (`patch`, `test`, `output`, `session_id`, `exit_code`); an
        unrecognised OTHER key rides along unread rather than failing the record,
        which a strict `extra="forbid"` sibling here would do.
    """

    model_config = OPEN_FOREIGN
    patch: str | None = None
    test: CombinedCommandResult | None = None
    output: str | None = None
    session_id: CodexShellId | int | None = None
    exit_code: int | None = None


class GoalToolResultBlock(BaseModel):
    """The goal fields that Codex control tools return.

    The result can also include budget and elapsed-use fields. Those fields do
    not change the canonical goal, so this boundary leaves them open and reads
    only the goal identity and state.
    """

    model_config = OPEN_FOREIGN
    objective: str | None = None
    status: str | None = None
    reason: str | None = None
