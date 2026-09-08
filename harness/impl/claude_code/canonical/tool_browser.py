# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate Claude Code browser tools."""

from domain.content import Content
from harness.impl.claude_code.canonical import records, support, tool_browser_values as browser_values


def _plain_action(action_name: str) -> str:
    return " ".join(action_name.removesuffix("_mcp").split("_")).capitalize()


def browser_action(native_name: str, arguments: records.ToolArguments) -> str:
    """Return a short browser action.

    Returns:
        The browser action.

    """
    tool_name = native_name.removeprefix(browser_values.CHROME_TOOL_PREFIX)
    if tool_name == "navigate" and arguments.url:
        return f"Navigate to {arguments.url}"
    if tool_name == "find":
        query = arguments.query or arguments.pattern
        if query:
            return f"Find {query} on page"
    if tool_name == "computer" and arguments.action:
        return _computer_action(arguments.action)
    return browser_values.CHROME_ACTIONS.get(tool_name, _plain_action(tool_name))


def _computer_action(native_action: str) -> str:
    action = native_action.strip().lower()
    if action == "screenshot":
        return "Capture browser screenshot"
    if action == "wait":
        return "Wait in browser"
    return f"{_plain_action(action)} in browser"


def browser_result_content(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
) -> Content | None:
    """Return browser text without binary image data.

    Returns:
        The browser content.

    """
    if not tool_response:
        return None
    native_result = _browser_native_result(tool_response)
    if isinstance(native_result, str):
        return support.content(native_result)
    if isinstance(native_result, records.ToolResponseBlocks):
        return _browser_blocks_content(native_result)
    return None


def _browser_native_result(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str,
) -> records.ToolResponseBlocks | str | None:
    if isinstance(tool_response, records.ToolResponse):
        return tool_response.result or tool_response.content
    return tool_response


def _browser_blocks_content(response: records.ToolResponseBlocks) -> Content | None:
    parts = [_browser_block_text(part) for part in response.root]
    text = "\n".join(part for part in parts if part).strip()
    return support.content(text) if text else None


def _browser_block_text(part: records.InnerContentBlock | str) -> str:
    if isinstance(part, str):
        return part
    if part.type == "image":
        return "[image]"
    return part.text or ""
