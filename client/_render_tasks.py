# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import _render_styles as styles
from _render_rows import (
    _RowOptions,
    rows,
)

if TYPE_CHECKING:
    from _model import (
        SessionModel,
        ShellFold,
        TaskRecord,
    )


def task_rows(model: SessionModel, width: int) -> list[str]:
    """Return the task rows.

    What is being worked on, in as few rows as it takes.

        Deleted tasks are dropped and completed ones are counted rather than listed:
        a finished item is not work, and the count is the only thing about it a reader
        still needs.

    Returns:
        Task rows.

    """
    tasks = [task for task in model.session.tasks if task.state != "deleted"]
    if not tasks:
        return []
    done = sum(1 for task in tasks if task.state == "completed")
    live = [task for task in tasks if task.state != "completed"]
    heading = f"tasks {int(done)}/{len(tasks)}"
    painted = rows(
        [styles.Span(f" {heading} ", styles.DARK, styles.MUTED, bold=True)],
        width,
        _RowOptions(mode=styles.TRUNCATE_LAYOUT),
    )
    painted.extend(_live_task_rows(live, width))
    return painted


def _live_task_rows(live: list[TaskRecord], width: int) -> list[str]:
    painted: list[str] = []
    for task in live[:styles.TASK_ROWS]:
        marker, color = styles.TASK_MARKERS.get(task.state, ("·", styles.MUTED))
        painted.extend(
            rows(
                [styles.Span(task.subject)],
                width,
                _RowOptions(
                    prefix=(styles.Span(f" {marker} ", color),),
                    continuation=(styles.Span("   "),),
                    mode=styles.TRUNCATE_LAYOUT,
                ),
            ),
        )
    remaining = len(live) - styles.TASK_ROWS
    if remaining > 0:
        painted.extend(
            rows(
                [styles.Span(f"… {int(remaining)} more", styles.DIM)],
                width,
                _RowOptions(mode=styles.TRUNCATE_LAYOUT),
            ),
        )
    return painted


def _shell_marker(fold: ShellFold) -> tuple[str, styles.Color, str]:
    if fold.execution == "monitor":
        return "▷", styles.WORKING, "monitor"
    if fold.execution == "background" or fold.backgrounded:
        return "▷", styles.WORKING, "background"
    return "▶", styles.TEXT, "foreground"


def _label(text: str, color: styles.Color) -> list[styles.Span]:
    return [styles.Span(f" {text} ", styles.DARK, color, bold=True)]


def _rule(width: int) -> str:
    return styles.Span("─" * width, styles.DIM).ansi()


def _said(label: str, text: str, width: int, color: styles.Color = styles.TEXT) -> list[str]:
    label_span = styles.Span(label + styles.TEXT_INDENT, color, bold=True)
    text_span = styles.Span(text)
    return rows(
        [label_span, text_span],
        width,
        _RowOptions(continuation=(styles.Span(styles.TEXT_INDENT),)),
    )
