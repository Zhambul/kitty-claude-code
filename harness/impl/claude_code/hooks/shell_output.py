# Copyright (c) 2026 Zhambyl Yermagambet
"""Build shell-output events from Claude Code hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.work_state import ShellFollowUntil
from harness.impl.claude_code.hooks import constants, foreground
from harness.models.raw_event_builders import output_location_raw_event
from repository.mapper.documents import encode_document

if TYPE_CHECKING:
    from domain.event_shell import ShellOutputLocated
    from harness.impl.claude_code.canonical.records import HookPayload
    from harness.models.raw_events import RawEvent, RawEventSourceContext


def shell_output_events(
    hook_payload: HookPayload,
    raw_event_source_context: RawEventSourceContext,
    reply: bytes,
) -> tuple[list[RawEvent], bytes]:
    """Build output-location events and return the current hook reply.

    Returns:
        The new raw events and the hook reply.

    """
    locations: tuple[ShellOutputLocated, ...] = ()
    if hook_payload.hook_event_name == "PreToolUse" and hook_payload.tool_name in {"Bash", "Monitor"}:
        locations, reply = _pretool_output(hook_payload, reply)
    elif hook_payload.hook_event_name in {"PostToolUse", "PostToolUseFailure"} and hook_payload.tool_name == "Bash":
        locations = _background_output(hook_payload)
    return (
        [
            output_location_raw_event(
                raw_event_source_context,
                constants.HARNESS,
                location,
                payload=encode_document(location),
            )
            for location in locations
        ],
        reply,
    )


def _pretool_output(
    hook_payload: HookPayload,
    reply: bytes,
) -> tuple[tuple[ShellOutputLocated, ...], bytes]:
    shell_arguments = hook_payload.shell_input()
    if hook_payload.tool_name == "Bash" and not shell_arguments.run_in_background:
        prepared = foreground.prepare(hook_payload)
        if prepared is not None:
            return prepared.locations, prepared.reply
        return (), reply
    return foreground.redirected_locations(hook_payload, ShellFollowUntil.SESSION_FINISHED), reply


def _background_output(hook_payload: HookPayload) -> tuple[ShellOutputLocated, ...]:
    background = foreground.background_output(hook_payload)
    return () if background is None else (background,)
