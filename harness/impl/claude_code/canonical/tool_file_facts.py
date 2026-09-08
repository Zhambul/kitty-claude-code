# Copyright (c) 2026 Zhambyl Yermagambet
"""Build Claude Code file facts."""

from domain import event_base, event_resource
from domain.outcomes import FileAction
from harness.impl.claude_code.canonical import records, support, tool_kind_values as kind_values
from harness.impl.claude_code.canonical.tool_patches import structured_patch
from harness.impl.claude_code.canonical.tool_result_models import FinishedToolIdentity, FinishedToolResult
from harness.models import raw_events


def file_facts(
    raw_event: raw_events.RawEvent,
    finished_tool_identity: FinishedToolIdentity,
    finished_tool_result: FinishedToolResult,
) -> list[event_base.CanonicalEvent[event_base.EventPayload]]:
    """Return file facts.

    Returns:
        The file facts.

    """
    action = kind_values.FILE_ACTIONS.get(finished_tool_identity.native_name)
    if action is None:
        return []
    path = finished_tool_identity.arguments.file_path or finished_tool_identity.arguments.notebook_path or ""
    if not path:
        return []
    content_value = _file_content(action, finished_tool_identity.arguments, finished_tool_result.response)
    patch = _file_patch(path, action, finished_tool_identity.arguments, finished_tool_result.response)
    payload = event_resource.FileAccessed(
        path,
        action,
        finished_tool_result.outcome,
        lines_added=patch[1],
        lines_removed=patch[2],
        unified_diff=patch[0],
        content=support.content(content_value) if content_value and patch[0] is None else None,
    )
    return [
        support.event(
            raw_event,
            support.CanonicalEventDraft(
                "file",
                f"{finished_tool_identity.call_id}:{action}:{path}",
                "accessed",
                payload,
            ),
        ),
    ]


def _file_content(
    file_action: FileAction,
    arguments: records.ToolArguments,
    tool_response: records.ToolResponse,
) -> str | records.ToolResponseBlocks | None:
    if file_action == FileAction.CREATED:
        return arguments.content
    if tool_response.file is not None and tool_response.file.content is not None:
        return tool_response.file.content
    if tool_response.content is not None:
        return tool_response.content
    return arguments.content


def _file_patch(
    path: str,
    file_action: FileAction,
    arguments: records.ToolArguments,
    tool_response: records.ToolResponse,
) -> tuple[str | None, int | None, int | None]:
    patch = structured_patch(path, tool_response)
    if file_action != FileAction.CREATED or patch[1] is not None:
        return patch
    if arguments.content is None:
        return patch
    return patch[0], len(arguments.content.splitlines()), patch[2]
