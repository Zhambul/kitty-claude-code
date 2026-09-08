# Copyright (c) 2026 Zhambyl Yermagambet
"""Actor statistics support."""

from __future__ import annotations

from dataclasses import replace
from itertools import starmap
from types import MappingProxyType
from typing import TYPE_CHECKING

from domain import (
    actor_state,
    event_actor,
    event_conversation,
    event_resource,
    event_session,
    event_shell,
    outcomes,
)

if TYPE_CHECKING:
    from domain import event_base

from engine.sessiondata.actor_status_work import _is_prompt

FILE_TOOLS = MappingProxyType({
    outcomes.FileAction.READ: "Read",
    outcomes.FileAction.CREATED: "Write",
    outcomes.FileAction.UPDATED: "Edit",
    outcomes.FileAction.DELETED: "Delete",
    outcomes.FileAction.RENAMED: "Move",
})


def _conversation_counted(
    actor_statistics: actor_state.ActorStatistics,
    event_payload: event_base.EventPayload,
) -> actor_state.ActorStatistics | None:
    if _is_prompt(event_payload):
        return replace(actor_statistics, prompt_count=actor_statistics.prompt_count + 1)
    if isinstance(event_payload, event_conversation.MessageCreated) and event_payload.recipient_actor_id is not None:
        return replace(actor_statistics, actor_message_count=actor_statistics.actor_message_count + 1)
    if isinstance(event_payload, event_shell.ShellStarted):
        return replace(actor_statistics, shell_command_count=actor_statistics.shell_command_count + 1)
    if isinstance(event_payload, event_shell.ShellFinished):
        return _finished_shell_count(actor_statistics, event_payload)
    return None


def _finished_shell_count(
    actor_statistics: actor_state.ActorStatistics,
    event_payload: event_shell.ShellFinished,
) -> actor_state.ActorStatistics:
    if event_payload.outcome == outcomes.Outcome.SUCCEEDED:
        return actor_statistics
    return replace(
        actor_statistics,
        failed_shell_command_count=actor_statistics.failed_shell_command_count + 1,
    )


def _tool_event_counted(
    actor_statistics: actor_state.ActorStatistics, event_payload: event_base.EventPayload,
) -> actor_state.ActorStatistics:
    if isinstance(event_payload, event_resource.FileAccessed):
        return _file_counted(actor_statistics, event_payload)
    if isinstance(event_payload, event_resource.SearchPerformed):
        return _tool_counted(actor_statistics, event_payload.tool)
    if isinstance(event_payload, event_resource.WebFetched):
        return _tool_counted(actor_statistics, "WebFetch")
    return _secondary_tool_event_counted(actor_statistics, event_payload)


def _secondary_tool_event_counted(
    actor_statistics: actor_state.ActorStatistics, event_payload: event_base.EventPayload,
) -> actor_state.ActorStatistics:
    if isinstance(event_payload, event_resource.BrowserInteracted):
        return _tool_counted(actor_statistics, "Browser")
    if isinstance(event_payload, event_resource.WorktreeChanged):
        return _tool_counted(
            actor_statistics,
            "EnterWorktree" if event_payload.action == outcomes.WorktreeAction.ENTERED else "ExitWorktree",
        )
    if isinstance(event_payload, event_resource.SkillStarted):
        return _tool_counted(actor_statistics, "Skill")
    return actor_statistics


def _file_counted(
    actor_statistics: actor_state.ActorStatistics, file_accessed: event_resource.FileAccessed,
) -> actor_state.ActorStatistics:
    paths = actor_statistics.file_paths_internal
    if file_accessed.path not in paths:
        paths = (*paths, file_accessed.path)
    return _tool_counted(
        replace(
            actor_statistics,
            file_paths_internal=paths,
            file_count=len(paths),
            lines_added=actor_statistics.lines_added + (file_accessed.lines_added or 0),
            lines_removed=actor_statistics.lines_removed + (file_accessed.lines_removed or 0),
        ),
        FILE_TOOLS[file_accessed.action],
    )


def _tool_counted(actor_statistics: actor_state.ActorStatistics, tool: str) -> actor_state.ActorStatistics:
    counts = {tool_count.tool: tool_count.count for tool_count in actor_statistics.tool_counts}
    counts[tool] = counts.get(tool, 0) + 1
    return replace(
        actor_statistics,
        tool_counts=tuple(starmap(actor_state.ToolCount, sorted(counts.items()))),
    )


def _timed(
    actor_statistics: actor_state.ActorStatistics, canonical_event: event_base.CanonicalEvent[event_base.EventPayload],
) -> actor_state.ActorStatistics:
    """Return the timed.

    One interval at a time: it opens when the actor has something to do and
        closes when the turn it was doing ends.

        A start event can open a new interval without a user prompt. Harnesses
        can continue work after a background notification. A command result
        alone does not reopen an interval that already ended.

    Returns:
        Timed.

    """
    payload = canonical_event.payload
    at = canonical_event.happened_at
    if actor_statistics.active_since_internal is None:
        if isinstance(
            payload,
            (
                event_session.SessionStarted,
                event_actor.ActorStarted,
                event_conversation.TurnStarted,
                event_shell.ShellStarted,
            ),
        ) or _is_prompt(payload):
            return replace(actor_statistics, active_since_internal=at)
        return actor_statistics
    if isinstance(
        payload, (event_conversation.TurnFinished, event_conversation.TurnAborted, event_session.SessionFinished),
    ):
        return replace(
            actor_statistics,
            active_seconds=actor_statistics.active_seconds + max(0, at - actor_statistics.active_since_internal),
            active_since_internal=None,
        )
    return actor_statistics
