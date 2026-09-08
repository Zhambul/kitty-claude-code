# Copyright (c) 2026 Zhambyl Yermagambet
"""Build Claude Code finished-tool answers."""

from domain.content import Content
from domain.outcomes import Outcome
from harness.impl.claude_code.canonical import records, support
from harness.impl.claude_code.canonical.tool_browser import browser_result_content
from harness.impl.claude_code.canonical.tool_kind_values import ToolKind
from harness.impl.claude_code.canonical.tool_result_models import FinishedToolIdentity, FinishedToolResult
from harness.impl.claude_code.canonical.tool_results import result_content, web_search_content


def finished_tool_result(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
    finished_tool_identity: FinishedToolIdentity,
    result: Content | None,
    *,
    failed: bool,
    cancelled: bool,
) -> FinishedToolResult:
    """Combine the native response, answer content, and completion state.

    Returns:
        The normalized tool result.

    """
    response = tool_response if isinstance(tool_response, records.ToolResponse) else records.ToolResponse()
    answer = finished_tool_answer(tool_response, finished_tool_identity, result)
    outcome = finished_tool_outcome(failed=failed, cancelled=cancelled)
    return FinishedToolResult(tool_response, response, answer, outcome, failed)


def finished_tool_outcome(*, failed: bool, cancelled: bool) -> Outcome:
    """Select a completion outcome from the native result flags.

    Returns:
        Cancelled before failed, or succeeded if neither flag is set.

    """
    if cancelled:
        return Outcome.CANCELLED
    if failed:
        return Outcome.FAILED
    return Outcome.SUCCEEDED


def finished_tool_answer(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
    finished_tool_identity: FinishedToolIdentity,
    result: Content | None,
) -> Content | None:
    """Select the most specific answer available for a finished tool.

    Returns:
        Search content, supplied result content, or a parsed native answer, if available.

    """
    search_answer = web_search_answer(tool_response, finished_tool_identity)
    if search_answer is not None:
        return search_answer
    if result is not None:
        return result
    if finished_tool_identity.kind == ToolKind.BROWSER:
        return browser_result_content(tool_response)
    return nonbrowser_tool_answer(tool_response, finished_tool_identity)


def nonbrowser_tool_answer(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
    finished_tool_identity: FinishedToolIdentity,
) -> Content | None:
    """Read a nonbrowser tool answer from its native response.

    Returns:
        Tool matches, file names, or general result content, if available.

    """
    tool_search_answer = tool_search_answer_for(tool_response, finished_tool_identity)
    if tool_search_answer is not None:
        return tool_search_answer
    filename_answer = filename_answer_for(tool_response, finished_tool_identity)
    if filename_answer is not None:
        return filename_answer
    return result_content(tool_response)


def web_search_answer(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
    finished_tool_identity: FinishedToolIdentity,
) -> Content | None:
    """Read structured results from a WebSearch response.

    Returns:
        Formatted search content, or None if this is not a structured WebSearch result.

    """
    if (
        finished_tool_identity.native_name == "WebSearch"
        and isinstance(tool_response, records.ToolResponse)
        and tool_response.search_results is not None
    ):
        return web_search_content(tool_response, str(finished_tool_identity.arguments.query or ""))
    return None


def tool_search_answer_for(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
    finished_tool_identity: FinishedToolIdentity,
) -> Content | None:
    """Read the tools matched by a ToolSearch response.

    Returns:
        The matched tool list or no-match message, or None for other response types.

    """
    if (
        finished_tool_identity.native_name == "ToolSearch"
        and isinstance(tool_response, records.ToolResponse)
        and tool_response.matches is not None
    ):
        loaded_tools = "\n".join(f"→ loaded tool: {tool_name}" for tool_name in tool_response.matches)
        return support.content(loaded_tools or "No matching tools.")
    return None


def filename_answer_for(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
    finished_tool_identity: FinishedToolIdentity,
) -> Content | None:
    """Read file names from a Grep or Glob response.

    Returns:
        One file name per line, or None if no file-name response is available.

    """
    if (
        finished_tool_identity.native_name in {"Grep", "Glob"}
        and isinstance(tool_response, records.ToolResponse)
        and tool_response.filenames is not None
    ):
        return support.content("\n".join(tool_response.filenames))
    return None
