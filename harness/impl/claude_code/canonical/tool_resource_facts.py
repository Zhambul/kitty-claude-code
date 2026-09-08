# Copyright (c) 2026 Zhambyl Yermagambet
"""Build Claude Code resource facts."""

from domain import event_base, event_resource
from domain.outcomes import WorktreeAction
from harness.impl.claude_code.canonical import support, tool_kind_values as kind_values
from harness.impl.claude_code.canonical.tool_browser import browser_action
from harness.impl.claude_code.canonical.tool_result_models import FinishedToolIdentity, FinishedToolResult
from harness.models import raw_events


def search_finished_fact(
    raw_event: raw_events.RawEvent,
    finished_tool_identity: FinishedToolIdentity,
    finished_tool_result: FinishedToolResult,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a search result and its first available query field.

    Returns:
        The canonical search event with its answer and outcome.

    """
    query = next(
        (
            getattr(finished_tool_identity.arguments, field_name)
            for field_name in kind_values.SEARCH_QUERY_FIELDS
            if getattr(finished_tool_identity.arguments, field_name)
        ),
        None,
    )
    payload = event_resource.SearchPerformed(
        finished_tool_identity.native_name,
        support.content(query),
        finished_tool_result.answer,
        finished_tool_result.outcome,
    )
    draft = support.CanonicalEventDraft(
        kind_values.ToolKind.SEARCH.value,
        finished_tool_identity.call_id,
        "performed",
        payload,
    )
    return support.event(raw_event, draft)


def web_finished_fact(
    raw_event: raw_events.RawEvent,
    finished_tool_identity: FinishedToolIdentity,
    finished_tool_result: FinishedToolResult,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a completed web fetch.

    Returns:
        The fetch event with its optional URL, answer, and outcome.

    """
    url = finished_tool_identity.arguments.url
    resource_url = None
    if url:
        resource_url = str(url)
    payload = event_resource.WebFetched(resource_url, finished_tool_result.answer, finished_tool_result.outcome)
    draft = support.CanonicalEventDraft(
        kind_values.ToolKind.WEB.value, finished_tool_identity.call_id, "fetched", payload,
    )
    return support.event(raw_event, draft)


def browser_finished_fact(
    raw_event: raw_events.RawEvent,
    finished_tool_identity: FinishedToolIdentity,
    finished_tool_result: FinishedToolResult,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a completed browser action.

    Returns:
        The browser event with the resolved action, answer, and outcome.

    """
    payload = event_resource.BrowserInteracted(
        browser_action(finished_tool_identity.native_name, finished_tool_identity.arguments),
        finished_tool_result.answer,
        finished_tool_result.outcome,
    )
    draft = support.CanonicalEventDraft(
        kind_values.ToolKind.BROWSER.value,
        finished_tool_identity.call_id,
        "interacted",
        payload,
    )
    return support.event(raw_event, draft)


def worktree_finished_fact(
    raw_event: raw_events.RawEvent,
    finished_tool_identity: FinishedToolIdentity,
    finished_tool_result: FinishedToolResult,
) -> event_base.CanonicalEvent[event_base.EventPayload]:
    """Map a worktree entry or exit operation.

    Returns:
        The worktree change event with its arguments and outcome.

    """
    action = WorktreeAction.ENTERED if finished_tool_identity.native_name == "EnterWorktree" else WorktreeAction.EXITED
    payload = event_resource.WorktreeChanged(
        action,
        support.content(finished_tool_identity.arguments) if finished_tool_identity.arguments else None,
        finished_tool_result.outcome,
    )
    draft = support.CanonicalEventDraft(
        kind_values.ToolKind.WORKTREE.value,
        finished_tool_identity.call_id,
        "changed",
        payload,
    )
    return support.event(raw_event, draft)
