# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from _render_rows import (
    _RowOptions,
    rows,
)
from _render_styles import (
    QUIET_FOR_THE_LEAD,
    TEXT_INDENT,
    WORKING,
    Span,
)
from _render_tools import _entry_text

if TYPE_CHECKING:
    from _model import (
        EntryBodyRecord,
        EntryRecord,
    )


def _assignment_rows(entry: EntryRecord, width: int) -> list[str]:
    marker, text = _assignment_content(entry)
    return rows(
        [Span(f"{marker} ", WORKING, bold=True), Span(text or "agent")],
        width,
        _RowOptions(continuation=(Span(TEXT_INDENT),)),
    )


def _assignment_content(entry: EntryRecord) -> tuple[str, str]:
    body = entry.body
    if entry.type == "assignment_started":
        return "⇢", _started_assignment_text(entry)
    return "⇠", _finished_assignment_text(body)


def _started_assignment_text(entry: EntryRecord) -> str:
    body = entry.body
    text = entry.summary or _entry_text(body.prompt)
    name = body.assigned_actor_name
    if name:
        return f"{name}: {text}" if text else name
    return text


def _finished_assignment_text(body: EntryBodyRecord) -> str:
    text = _entry_text(body.result)
    if body.state != "succeeded":
        return f"{body.state} · {text}" if text else body.state or ""
    return text


def visible(entry: EntryRecord, lead_actor_id: str) -> bool:
    if entry.type not in QUIET_FOR_THE_LEAD:
        return True
    if entry.body.role == "system":
        return False
    return entry.actor_id != lead_actor_id
