# Copyright (c) 2026 Zhambyl Yermagambet
"""Split terminal mirror rendering."""

from __future__ import annotations

from typing import TYPE_CHECKING

from _render_blocks import (
    _block,
    _BlockContent,
)
from _render_numbers import duration
from _render_styles import (
    DIM,
    FAILURE,
    SUCCESS,
    TEXT,
    Links,
    Span,
)
from _render_tasks import (
    _label,
    _shell_marker,
)

if TYPE_CHECKING:
    from _model import (
        ShellFold,
    )


def _shell_rows(
    fold: ShellFold,
    copy: Links,
    width: int,
    *,
    running: bool,
) -> list[str]:
    marker, color, heading = _shell_marker(fold)
    finish = _shell_finish(fold, running=running, heading=heading)
    links = []
    if fold.command:
        links.append(_copy_span(copy, fold.shell_id, "cmd", "⧉cmd"))
    if fold.output or fold.status:
        links.append(_copy_span(copy, fold.shell_id, "out", "⧉out"))
    return _block(
        f"{marker} {heading}",
        color,
        _BlockContent(fold.command, fold.output, fold.status, finish, links),
        width,
    )


def _copy_span(copy: Links, subject_id: str, part: str, label: str) -> Span:
    target = copy_target(subject_id, part)
    return Span(label, DIM, link=copy(target))


def _shell_finish(
    fold: ShellFold,
    *,
    running: bool,
    heading: str,
) -> list[Span] | None:
    if not running and fold.state is not None:
        elapsed = _shell_elapsed(fold)
        if fold.state == "succeeded":
            text = "■ finished"
            finish_color = TEXT if heading == "foreground" else SUCCESS
        else:
            text = f"■ {fold.state}"
            if fold.exit_code:
                text = f"{text} (exit {int(fold.exit_code)})"
            finish_color = FAILURE
        if elapsed:
            text = f"{text} · {elapsed}"
        return _label(text, finish_color)
    return None


def _shell_elapsed(fold: ShellFold) -> str:
    if fold.finished_at is None:
        return ""
    elapsed_seconds = max(0, fold.finished_at - fold.started_at)
    return duration(elapsed_seconds)


def copy_target(shell_id: str, half: str) -> str:
    """Return the copy target.

    The name a copy link carries, and the key the pane publishes it under.

        Two halves per command because they are two things a person copies: what was
        RUN and what came BACK. They were two content references before and they are
        two names now; nothing else changed.

    Returns:
        Copy target.

    """
    return f"sh:{shell_id}:{half}"
