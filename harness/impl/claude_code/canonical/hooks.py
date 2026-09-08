# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code hook-stream events."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.impl.claude_code.canonical import (
    hook_actors,
    hook_lifecycle,
    hook_tools,
    records,
)

if TYPE_CHECKING:
    from domain.event_base import CanonicalEvent, EventPayload
    from harness.impl.claude_code.canonical.toolcalls import ToolCallSemantics
    from harness.impl.claude_code.canonical.turns import TurnSemantics
    from harness.models.raw_events import RawEvent
    from harness.models.selections import SelectionSemantics

effort_report = hook_lifecycle.effort_report
turn_finished = hook_lifecycle.turn_finished


def translate_hook(
    raw_event: RawEvent,
    hook: records.HookPayload,
    tool_call_semantics: ToolCallSemantics,
    turn_semantics: TurnSemantics,
    selection_semantics: SelectionSemantics,
) -> list[CanonicalEvent[EventPayload]]:
    """Translate one Claude Code hook.

    Returns:
        The translated events.

    """
    translated = hook_lifecycle.lifecycle_hook_events(
        raw_event,
        hook,
        turn_semantics,
        selection_semantics,
    )
    if translated is not None:
        return translated
    translated = hook_tools.tool_hook_events(
        raw_event,
        hook,
        tool_call_semantics,
        selection_semantics,
    )
    if translated is not None:
        return translated
    return hook_actors.actor_hook_events(raw_event, hook, selection_semantics)
