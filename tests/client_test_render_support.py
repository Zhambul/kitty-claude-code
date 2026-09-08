# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify terminal client architecture and behavior."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from tests.client_test_models import (
    PaneFeedRecord,
    PaneModel,
    lead_pane_entry,
)

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path
    from types import ModuleType

TYPE_FIELD = "type"


CURSOR_FIELD = "cursor"


ACTOR_ID_FIELD = "actor_id"


LEAD_ACTOR_ID_TEXT = "lead"


CONTENT_FIELD = "content"


TEXT_FIELD = "text"


STATE_FIELD = "state"


SESSION_FIELD = "session"


SESSION_ID_FIELD = "session_id"


TEST_SESSION_ID_TEXT = "session-one"


LEAD_ACTOR_ID_FIELD = "lead_actor_id"


ACCOUNT_FIELD = "account"


ACTORS_FIELD = "actors"


LIVE_FIELD = "live"


TEXT_ENCODING = "utf-8"


RESIZE_AMOUNT = "9"


type JsonValue = bool | float | int | str | list[JsonValue] | dict[str, JsonValue] | None


def pane_prompt(entry_id: str, reply_to: str) -> dict[str, JsonValue]:
    """Make a prompt linked to a parent entry.

    Returns:
        The prompt entry document.

    """
    return lead_pane_entry(
        entry_id,
        "message",
        {
            "role": "user",
            "phase": "prompt",
            CONTENT_FIELD: {TEXT_FIELD: f"ask {entry_id}"},
            "reply_to": reply_to,
        },
    )


def discarded_parent_prompts() -> list[dict[str, JsonValue]]:
    """Return two prompts where the newer prompt replaces the older one.

    Returns:
        Two prompts where the newer prompt replaces the older one.

    """
    return [pane_prompt("8", "parent-1"), pane_prompt(RESIZE_AMOUNT, "parent-1")]


def pane_message_ids(model: PaneModel) -> list[str]:
    """Read the message identifiers from the pane.

    Returns:
        The identifiers in feed order.

    """
    return [feed_record.entry_id for feed_record in _pane_messages(model)]


def _pane_messages(model: PaneModel) -> Iterator[PaneFeedRecord]:
    for feed_record in model.feed():
        if getattr(feed_record, TYPE_FIELD, None) == "message":
            yield feed_record


def task_record(task_id: str, subject: str, state: str) -> dict[str, JsonValue]:
    """Make a task with no assigned owner.

    Returns:
        The task document.

    """
    return {
        "task_id": task_id,
        "subject": subject,
        "description": None,
        STATE_FIELD: state,
        "owner_actor_id": None,
    }


def scoreboard_with(
    model_module: ModuleType,
    render: ModuleType,
    *,
    active: bool,
) -> tuple[PaneModel, ModuleType]:
    """Set up the actor statistics for a rendering test.

    Returns:
        The pane model and its rendering module.

    """
    model = model_module.SessionModel()
    model.apply_snapshot(
        {
            CURSOR_FIELD: 1,
            SESSION_FIELD: {
                SESSION_ID_FIELD: TEST_SESSION_ID_TEXT,
                LEAD_ACTOR_ID_FIELD: LEAD_ACTOR_ID_TEXT,
                ACCOUNT_FIELD: None,
            },
            ACTORS_FIELD: [
                {
                    ACTOR_ID_FIELD: LEAD_ACTOR_ID_TEXT,
                    "name": "Lead",
                    "background": {},
                    "usage": {"tokens": {}, "cost_in_usd": None},
                    "statistics": {"active_seconds": 100.0, "active": active},
                },
            ],
            LIVE_FIELD: True,
        },
    )
    return model, render


def imported_names(path: Path) -> Iterator[str]:
    """Read imported module names from a Python file.

    Yields:
        Each module name from an import statement.

    """
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module
