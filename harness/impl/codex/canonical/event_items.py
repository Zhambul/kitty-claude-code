
# Copyright (c) 2026 Zhambyl Yermagambet
"""Convert completed Codex event items."""

from harness.impl.codex.canonical import (
    event_file_changes,
)

# Keep event conversion separate from foreign record models.
# isort: split

from harness.impl.codex.canonical import (
    record_actor_records,
    record_collaboration_items,
    record_file_items,
    record_interaction_records,
    record_item_registry,
    record_mcp_items,
    record_terminal_records,
    record_tool_records,
)
from harness.impl.codex.canonical.vocabulary import empty_record
from harness.impl.codex.ids_conversation_types import CodexTurnId
from harness.impl.codex.ids_session_types import CodexActorId, CodexCallId, CodexShellId

OPERATION_ITEM_TYPES = (
    record_file_items.FileChangeItem,
    record_file_items.CommandExecutionItem,
    record_collaboration_items.SubAgentActivityItem,
)


def command_execution(
    command_item: record_file_items.CommandExecutionItem,
    turn_id: CodexTurnId | None,
) -> record_tool_records.CommandCompletedRecord | None:
    """Convert one completed command.

    Returns:
        The completed command, or None if it has no process identity.

    """
    if command_item.process_id is None:
        return None
    output = command_item.aggregated_output
    if output is None:
        output = command_item.formatted_output
    if output is None:
        output = "".join((command_item.stdout or "", command_item.stderr or ""))
    return record_tool_records.CommandCompletedRecord(
        process_id=CodexShellId(str(command_item.process_id)),
        command=tuple(command_item.command or ()),
        output=output,
        exit=command_item.exit_code,
        item_id=command_item.id or "",
        turn=turn_id,
    )


def subagent_activity(
    activity_item: record_collaboration_items.SubAgentActivityItem,
    payload: record_item_registry.ItemCompletedPayload,
) -> record_actor_records.ActorActivityRecord | None:
    """Convert one subagent activity item.

    Returns:
        The actor activity, or None if it has no actor identity.

    """
    actor_id = activity_item.agent_thread_id
    if not actor_id:
        return None
    started_at = (payload.started_at_ms or 0) / 1000 or None
    return record_actor_records.ActorActivityRecord(
        activity=activity_item.kind or "",
        actor_id=CodexActorId(actor_id),
        call_id=CodexCallId(activity_item.id or ""),
        turn=payload.turn_id or "",
        at=started_at,
    )


def mcp_result_text(result: record_mcp_items.McpToolCallResult | None) -> str:
    """Return the text from an MCP result.

    Returns:
        The result text.

    """
    if result is None:
        return ""
    result_parts: list[str] = []
    for result_part in result.content or ():
        if isinstance(result_part, str):
            result_parts.append(result_part)
        else:
            result_parts.append(result_part.text or "")
    return "\n".join(result_parts).strip()


def mcp_completed(mcp_item: record_mcp_items.McpToolCallItem) -> record_terminal_records.RolloutRecord:
    """Convert one completed MCP call.

    Returns:
        The completed MCP record or a covered-item record.

    """
    if not mcp_item.server or not mcp_item.tool or not mcp_item.status:
        return record_terminal_records.CoveredItemRecord()
    result = mcp_item.result
    return record_tool_records.McpToolCompletedRecord(
        server=mcp_item.server,
        tool=mcp_item.tool,
        status=mcp_item.status,
        item_id=mcp_item.id or "",
        title=mcp_item.arguments.title if mcp_item.arguments else None,
        result=mcp_result_text(result) or None,
        result_is_error=result.is_error if result else False,
        browser_use=bool(result and result.metadata and result.metadata.browser_use),
    )


def operation_item(
    operation: record_file_items.FileChangeItem
    | record_file_items.CommandExecutionItem
    | record_collaboration_items.SubAgentActivityItem,
    payload: record_item_registry.ItemCompletedPayload,
) -> record_terminal_records.RolloutRecord | None:
    """Convert one operation item.

    Returns:
        The operation record, or None if the operation is incomplete.

    """
    if isinstance(operation, record_file_items.FileChangeItem):
        return event_file_changes.file_change(operation)
    if isinstance(operation, record_file_items.CommandExecutionItem):
        return command_execution(operation, payload.turn_id)
    return subagent_activity(operation, payload)


def content_item(
    completed_item: record_mcp_items.CoveredItem
    | record_collaboration_items.CollabAgentToolCallItem
    | record_collaboration_items.PlanItem,
) -> record_terminal_records.RolloutRecord:
    """Convert one completed content item.

    Returns:
        The canonical content record.

    """
    if isinstance(completed_item, (record_mcp_items.CoveredItem, record_collaboration_items.CollabAgentToolCallItem)):
        return record_terminal_records.CoveredItemRecord()
    plan_text = (completed_item.text or "").strip()
    if plan_text:
        return record_interaction_records.PlanRecord(text=plan_text, id=completed_item.id or "")
    return empty_record()


def item_completed(payload: record_item_registry.ItemCompletedPayload) -> record_terminal_records.RolloutRecord | None:
    """Convert one completed Codex item.

    Returns:
        The completed item record, or None for an unknown item.

    Raises:
        TypeError: If the item does not match its declared model.

    """
    completed_item = payload.completed_item
    if completed_item is None:
        return None
    item_type = record_item_registry.ItemCompletedType(completed_item.type)
    expected_model = record_item_registry.ITEM_COMPLETED_ITEMS[item_type]
    if not isinstance(completed_item, expected_model):
        message = f"Codex item {completed_item.type!r} did not match {expected_model.__name__}"
        raise TypeError(message)
    if isinstance(completed_item, OPERATION_ITEM_TYPES):
        return operation_item(completed_item, payload)
    if isinstance(completed_item, record_mcp_items.McpToolCallItem):
        return mcp_completed(completed_item)
    return content_item(completed_item)
