# Copyright (c) 2026 Zhambyl Yermagambet
"""Classify Claude Code tools."""

from harness.impl.claude_code.canonical import tool_kind_values as kind_values
from harness.models.raw_events import UnknownRawEventError


def tool_kind(native_name: str) -> kind_values.ToolKind:
    """Return the canonical tool kind.

    Returns:
        The tool kind.

    Raises:
        UnknownRawEventError: If the native tool is not mapped.

    """
    if native_name.startswith("mcp__claude-in-chrome__"):
        return kind_values.ToolKind.BROWSER
    kind = kind_values.TOOL_KINDS.get(native_name)
    if kind is None:
        reported_name = native_name or "<missing>"
        msg = f"unmapped Claude Code tool: {reported_name}"
        raise UnknownRawEventError(msg)
    return kind
