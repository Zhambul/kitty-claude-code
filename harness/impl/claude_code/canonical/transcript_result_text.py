# Copyright (c) 2026 Zhambyl Yermagambet
"""Read text from Claude tool results."""

from harness.impl.claude_code.canonical import records


def result_text(content: str | list[records.InnerContentBlock | str] | None) -> str:
    """Convert tool-result content to text.

    Returns:
        The normalized text.

    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [result_block_text(content_block) for content_block in content]
        return "\n".join(part for part in parts if part)
    return str(content)


def result_block_text(content_block: records.InnerContentBlock | str) -> str:
    """Convert one tool-result block to text.

    Returns:
        The normalized block text.

    """
    if isinstance(content_block, str):
        return content_block
    if content_block.type == "text" or isinstance(content_block.text, str):
        return content_block.text or ""
    if content_block.type == "tool_reference":
        tool_name = content_block.tool_name or ""
        return f"→ loaded tool: {tool_name}"
    if content_block.type == "image":
        return "[image]"
    return content_block.model_dump_json(exclude_none=True)
