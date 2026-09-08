# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from _render_blocks import (
    _block,
    _BlockContent,
)
from _render_styles import (
    FAILURE,
    TEXT,
    Span,
)
from _render_tasks import _label

if TYPE_CHECKING:
    from _model import (
        ContentRecord,
        EntryRecord,
    )


def _tool_rows(entry: EntryRecord, width: int) -> list[str]:
    """Return the tool rows.

    A search, a fetch, a worktree move or a skill — the block shape with the
        tool's own name on the chip. These arrived as one operation kind each in the
        old vocabulary and drew as commands; they still do.

    Returns:
        Tool rows.

    """
    body = entry.body
    chip, summary = _tool_summary(entry)
    finish = _tool_finish(body.state)
    return _block(
        chip,
        TEXT,
        _BlockContent(summary, _entry_text(body.result), "", finish),
        width,
    )


def _tool_finish(state: str | None) -> list[Span] | None:
    if state in {None, "succeeded"}:
        return None
    return _label(f"■ {state}", FAILURE)


def _tool_summary(entry: EntryRecord) -> tuple[str, str]:
    body = entry.body
    if entry.type == "search":
        return body.tool or "search", _entry_text(body.query)
    if entry.type == "web":
        return "WebFetch", body.url or ""
    if entry.type == "browser":
        return "Browser", body.action or ""
    if entry.type == "worktree":
        chip = "EnterWorktree" if body.action == "entered" else "ExitWorktree"
        return chip, _entry_text(body.arguments)
    return (
        ("Skill", body.name or "")
        if entry.type == "skill_started"
        else ("Skill finished", "")
    )


def _entry_text(content: ContentRecord | None) -> str:
    return "" if content is None else content.text
