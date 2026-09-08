# Copyright (c) 2026 Zhambyl Yermagambet
"""Validate content-bearing session entries."""

from __future__ import annotations

from types import MappingProxyType
from typing import Final

from domain.content import Content, content_text
from domain.entries import EntryTypeName, SessionEntry
from domain.entry_base import EntryBody, FileState
from domain.entry_conversation import MessageBody, ReasoningBody
from domain.entry_resources import BrowserBody, FileBody, SearchBody, WebBody
from domain.entry_shells import ShellOutputBody
from domain.outcomes import FileAction

CONTENT_FIELD = "content"
EMPTY_BODY_SUSPECT: Final = MappingProxyType({
    EntryTypeName.MESSAGE: CONTENT_FIELD,
    EntryTypeName.REASONING: CONTENT_FIELD,
    EntryTypeName.SHELL_OUTPUT: CONTENT_FIELD,
    EntryTypeName.FILE: CONTENT_FIELD,
    EntryTypeName.SEARCH: "result",
    EntryTypeName.WEB: "result",
    EntryTypeName.BROWSER: "result",
})


def _content_field(entry_body: EntryBody) -> Content | None:
    if isinstance(entry_body, MessageBody):
        return entry_body.content
    if isinstance(entry_body, ReasoningBody):
        return entry_body.content
    if isinstance(entry_body, ShellOutputBody):
        return entry_body.content
    if isinstance(entry_body, FileBody):
        return entry_body.content
    return _result_content(entry_body)


def _result_content(entry_body: EntryBody) -> Content | None:
    if isinstance(entry_body, SearchBody):
        return entry_body.result
    if isinstance(entry_body, WebBody):
        return entry_body.result
    if isinstance(entry_body, BrowserBody):
        return entry_body.result
    return None


def has_empty_required_body(session_entry: SessionEntry) -> bool:
    """Return true when a content-bearing entry has no useful content.

    Returns:
        True when a content-bearing entry has no useful content.

    """
    if session_entry.entry_type not in EMPTY_BODY_SUSPECT:
        return False
    if isinstance(session_entry.body, FileBody) and (
        session_entry.body.action == FileAction.RENAMED or session_entry.body.state == FileState.FAILED
    ):
        return False
    content = _content_field(session_entry.body)
    if isinstance(session_entry.body, ShellOutputBody):
        return content is not None and not content_text(content)
    return content is not None and not content_text(content).strip()
