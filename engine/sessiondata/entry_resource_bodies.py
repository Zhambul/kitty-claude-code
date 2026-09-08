# Copyright (c) 2026 Zhambyl Yermagambet
"""Create feed bodies for resource events."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import content, entry_base, entry_resources, event_resource, outcomes

if TYPE_CHECKING:
    from domain import event_base


def resource_body(event_payload: event_base.EventPayload) -> entry_base.EntryBody | None:
    """Return the resource-event body.

    Returns:
        The entry body, or none when the event is not a resource event.

    """
    resource_event_types = (
        event_resource.FileAccessed,
        event_resource.SearchPerformed,
        event_resource.WebFetched,
        event_resource.BrowserInteracted,
        event_resource.WorktreeChanged,
    )
    if not isinstance(event_payload, resource_event_types):
        return None
    state = file_state(event_payload.outcome)
    return mapped_resource_body(event_payload, state)


def file_state(outcome: outcomes.Outcome) -> entry_base.FileState:
    """Return the file state.

    Returns:
        The file state.

    """
    return entry_base.FileState.SUCCEEDED if outcome == outcomes.Outcome.SUCCEEDED else entry_base.FileState.FAILED


def mapped_resource_body(
    event_payload: (
        event_resource.FileAccessed
        | event_resource.SearchPerformed
        | event_resource.WebFetched
        | event_resource.BrowserInteracted
        | event_resource.WorktreeChanged
    ),
    state: entry_base.FileState,
) -> entry_base.EntryBody:
    """Return the body for one resource event.

    Returns:
        The entry body.

    """
    if isinstance(event_payload, event_resource.FileAccessed):
        return entry_resources.FileBody(
            path=event_payload.path,
            action=event_payload.action,
            state=state,
            previous_path=event_payload.previous_path,
            line_start=event_payload.line_start,
            line_end=event_payload.line_end,
            lines_added=event_payload.lines_added,
            lines_removed=event_payload.lines_removed,
            content=event_payload.content if event_payload.unified_diff is None else diff(event_payload),
        )
    if isinstance(event_payload, event_resource.SearchPerformed):
        return entry_resources.SearchBody(event_payload.tool, event_payload.query, state, event_payload.result)
    if isinstance(event_payload, event_resource.WebFetched):
        return entry_resources.WebBody(event_payload.url, state, event_payload.result)
    if isinstance(event_payload, event_resource.BrowserInteracted):
        return entry_resources.BrowserBody(event_payload.action, state, event_payload.result)
    return entry_resources.WorktreeBody(event_payload.action, state, event_payload.arguments)


def diff(file_accessed: event_resource.FileAccessed) -> content.TextContent:
    """Return the file diff as text content.

    Returns:
        The diff content.

    """
    return content.TextContent(file_accessed.unified_diff or "", content.MediaType.TEXT_PLAIN)
