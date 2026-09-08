# Copyright (c) 2026 Zhambyl Yermagambet
"""Create feed entry summaries."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import content, event_actor, event_shell

if TYPE_CHECKING:
    from domain import event_base


def summary(event_payload: event_base.EventPayload) -> str | None:
    """Return the entry summary.

    Returns:
        The summary, or none when the event has no summary.

    """
    if isinstance(event_payload, event_shell.ShellStarted):
        return event_payload.description
    if isinstance(event_payload, event_actor.ActorAssignmentStarted):
        return content.content_text(event_payload.brief) or None
    return None
