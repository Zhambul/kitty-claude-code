# Copyright (c) 2026 Zhambyl Yermagambet
"""Create feed bodies for model and effort selections."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import entry_base, entry_lifecycle, event_session

if TYPE_CHECKING:
    from domain import event_base, ids
    from engine.sessiondata import naming


def selection_body(
    event_payload: event_base.EventPayload,
    harness: ids.HarnessName,
    model_naming: naming.ModelNaming,
) -> entry_base.EntryBody | None:
    """Return the selection body.

    Returns:
        The entry body, or none when no selection body applies.

    """
    if isinstance(event_payload, event_session.ModelChanged):
        if not is_switch(event_payload):
            return None
        return entry_lifecycle.ModelChangeBody(
            model_naming.display(harness, event_payload.current),
            None if event_payload.previous is None else model_naming.display(harness, event_payload.previous),
            event_payload.reason == "automatic_fallback",
        )
    if isinstance(event_payload, event_session.EffortChanged):
        if event_payload.previous is None or event_payload.previous == event_payload.current:
            return None
        return entry_lifecycle.EffortChangeBody(event_payload.current, event_payload.previous)
    return None


def is_switch(model_changed: event_session.ModelChanged) -> bool:
    """Return true when a model change is a user-visible switch.

    Returns:
        True if the change is a switch; otherwise, false.

    """
    previous, current = model_changed.previous, model_changed.current
    if previous is None or "<synthetic>" in {previous.name, current.name}:
        return False
    return previous.name != current.name
