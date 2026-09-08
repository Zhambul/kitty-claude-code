# Copyright (c) 2026 Zhambyl Yermagambet
"""Own item registry models."""

from __future__ import annotations

from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field

from harness.impl.codex.canonical.record_collaboration_items import (
    CollabAgentToolCallItem,
    PlanItem,
    SubAgentActivityItem,
)
from harness.impl.codex.canonical.record_config import FOREIGN, OPEN_FOREIGN
from harness.impl.codex.canonical.record_file_items import CommandExecutionItem, FileChangeItem
from harness.impl.codex.canonical.record_mcp_items import CoveredItem, McpToolCallItem
from harness.impl.codex.ids_conversation_types import CodexTurnId
from harness.impl.codex.ids_session_types import CodexSessionId

if TYPE_CHECKING:
    from collections.abc import Mapping

type ItemCompletedItem = (
    FileChangeItem
    | CommandExecutionItem
    | SubAgentActivityItem
    | CollabAgentToolCallItem
    | PlanItem
    | McpToolCallItem
    | CoveredItem
)


class ItemCompletedType(StrEnum):
    """Represent item completed type."""

    FILE_CHANGE = "FileChange"
    COMMAND_EXECUTION = "CommandExecution"
    SUBAGENT_ACTIVITY = "SubAgentActivity"
    COLLAB_AGENT_TOOL_CALL = "CollabAgentToolCall"
    PLAN = "Plan"
    USER_MESSAGE = "UserMessage"
    AGENT_MESSAGE = "AgentMessage"
    REASONING = "Reasoning"
    MCP_TOOL_CALL = "McpToolCall"
    CONTEXT_COMPACTION = "ContextCompaction"
    EXTENSION = "Extension"
    IMAGE_VIEW = "ImageView"


ITEM_COMPLETED_ITEMS: Mapping[ItemCompletedType, type[ItemCompletedItem]] = MappingProxyType({
    ItemCompletedType.FILE_CHANGE: FileChangeItem,
    ItemCompletedType.COMMAND_EXECUTION: CommandExecutionItem,
    ItemCompletedType.SUBAGENT_ACTIVITY: SubAgentActivityItem,
    ItemCompletedType.COLLAB_AGENT_TOOL_CALL: CollabAgentToolCallItem,
    ItemCompletedType.PLAN: PlanItem,
    ItemCompletedType.USER_MESSAGE: CoveredItem,
    ItemCompletedType.AGENT_MESSAGE: CoveredItem,
    ItemCompletedType.REASONING: CoveredItem,
    ItemCompletedType.MCP_TOOL_CALL: McpToolCallItem,
    ItemCompletedType.CONTEXT_COMPACTION: CoveredItem,
    ItemCompletedType.EXTENSION: CoveredItem,
    ItemCompletedType.IMAGE_VIEW: CoveredItem,
})


CompletedItem = Annotated[
    FileChangeItem
    | CommandExecutionItem
    | SubAgentActivityItem
    | CollabAgentToolCallItem
    | PlanItem
    | McpToolCallItem
    | CoveredItem,
    Field(discriminator="type"),
]


class ItemCompletedPayload(BaseModel):
    """Represent item completed payload."""

    model_config = FOREIGN
    type: Literal["item_completed"] = "item_completed"
    turn_id: CodexTurnId | None = None
    started_at_ms: int | None = None
    completed_at_ms: int | None = None
    thread_id: CodexSessionId | None = None
    completed_item: CompletedItem | None = Field(default=None, alias="item")


class ItemTypeHeader(BaseModel):
    """Represent item type header."""

    model_config = OPEN_FOREIGN
    type: str | None = None
