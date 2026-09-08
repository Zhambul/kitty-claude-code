# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude tool hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.claude_code.canonical import hook_lifecycle, records
from harness.impl.claude_code.ids import ClaudeCodeShellId

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.impl.claude_code.canonical.toolcalls import ToolCallSemantics
    from harness.models.raw_events import RawEvent
    from harness.models.selections import SelectionSemantics


def tool_hook_events(
    raw_event: RawEvent,
    hook: records.HookPayload,
    tool_call_semantics: ToolCallSemantics,
    selection_semantics: SelectionSemantics,
) -> list[CanonicalEvent[EventPayload]] | None:
    """Translate a tool hook.

    Returns:
        The translated events, or None for another hook group.

    """
    hook_name = hook.hook_event_name or ""
    if hook_name == "PreToolUse":
        return [
            *tool_call_semantics.tool_started(
                raw_event,
                records.ToolCallNative(
                    tool_use_id=hook.tool_use_id,
                    tool_name=hook.tool_name,
                    tool_input=hook.tool_input,
                ),
            ),
            *hook_lifecycle.effort_report(
                raw_event,
                hook,
                selection_semantics,
            ),
        ]
    if hook_name in {"PostToolUse", "PostToolUseFailure"}:
        return _post_tool_hook_events(
            raw_event,
            hook,
            hook_name,
            tool_call_semantics,
            selection_semantics,
        )
    return None


def _post_tool_hook_events(
    raw_event: RawEvent,
    hook: records.HookPayload,
    hook_name: str,
    tool_call_semantics: ToolCallSemantics,
    selection_semantics: SelectionSemantics,
) -> list[CanonicalEvent[EventPayload]]:
    if hook_name == "PostToolUse" and hook.tool_name == "TaskStop":
        events = tool_call_semantics.background_stopped(
            raw_event,
            task_id=ClaudeCodeShellId(
                str("" if hook.tool_input is None else hook.tool_input.task_id),
            ),
            transcript_path=str(hook.transcript_path or ""),
        )
    else:
        events = tool_call_semantics.tool_finished(
            raw_event,
            records.ToolCallNative(
                tool_use_id=hook.tool_use_id,
                tool_name=hook.tool_name,
                tool_input=hook.tool_input,
                tool_response=(hook.error if hook.tool_response is None else hook.tool_response),
            ),
            failed=hook_name == "PostToolUseFailure",
        )
    return [
        *events,
        *hook_lifecycle.effort_report(raw_event, hook, selection_semantics),
    ]
