# Copyright (c) 2026 Zhambyl Yermagambet
"""Translate generic Claude Code tool results."""

from domain.content import Content
from harness.impl.claude_code.canonical import records, support


def result_content(
    tool_response: records.ToolResponse | records.ToolResponseBlocks | str | None,
) -> Content | None:
    """Return generic result content.

    Returns:
        The result content.

    """
    if not tool_response:
        return None
    if isinstance(tool_response, records.ToolResponse):
        native_result = tool_response.result or tool_response.content
        if isinstance(native_result, str):
            return support.content(native_result)
    return support.content(tool_response)


def web_search_content(tool_response: records.ToolResponse, fallback_query: str) -> Content:
    """Return WebSearch content.

    Returns:
        The search content.

    """
    query = tool_response.query or fallback_query
    links, answers = _web_search_parts(tool_response)
    parts = [f'Web search results for query: "{query}"']
    if links:
        rendered_links = "\n".join(links)
        parts.append(f"Links:\n{rendered_links}")
    parts.extend(answers)
    return support.content("\n\n".join(parts))


def _web_search_parts(tool_response: records.ToolResponse) -> tuple[list[str], list[str]]:
    links: list[str] = []
    answers: list[str] = []
    for result in tool_response.search_results or ():
        if isinstance(result, str):
            if result.strip():
                answers.append(result.strip())
            continue
        links.extend(_web_search_links(result))
    return links, answers


def _web_search_links(result: records.WebSearchResultSet) -> list[str]:
    links: list[str] = []
    for link in result.content or ():
        title = (link.title or link.url or "").strip()
        url = (link.url or "").strip()
        if title and url:
            links.append(f"- {title} — {url}")
        elif title:
            links.append(f"- {title}")
    return links
