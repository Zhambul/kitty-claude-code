# Copyright (c) 2026 Zhambyl Yermagambet
"""Polling checks for compaction lifecycle state."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata.models.entry import CompactionFinishedBodyResponse

if TYPE_CHECKING:
    from sdk.state import CompactionState, SessionSnapshot
    from tests.e2e.testkit.references import CompactionRef


def compaction(snapshot: SessionSnapshot, reference: CompactionRef) -> CompactionState:
    """Return the compaction with the specified identity.

    Returns:
        The single matching compaction.

    Raises:
        AssertionError: If the identity does not select one compaction.

    """
    matches = [
        compaction_state
        for compaction_state in snapshot.compactions()
        if compaction_state.actor_id == reference.actor_id
        and compaction_state.started_cursor == reference.started_cursor
    ]
    if len(matches) != 1:
        message = f"compaction at cursor {reference.started_cursor} has {len(matches)} matches"
        raise AssertionError(message)
    return matches[0]


def is_finished(snapshot: SessionSnapshot, reference: CompactionRef) -> bool | None:
    """Return true when the compaction is finished.

    Returns:
        True when finished, or None while in progress.

    """
    return True if compaction(snapshot, reference).finished else None


def actor_is_ready(snapshot: SessionSnapshot, reference: CompactionRef) -> bool | None:
    """Return true when the compaction actor is ready.

    Returns:
        True when ready, or None while compacting.

    """
    lifecycle = compaction(snapshot, reference)
    if lifecycle.finished and not snapshot.actor(reference.actor_id).context.compacting:
        return True
    return None


def has_one_finished_entry(
    snapshot: SessionSnapshot,
    reference: CompactionRef,
    name: str,
) -> bool | None:
    """Check that the finished compaction has one feed entry.

    Returns:
        True after the check, or None while the compaction is in progress.

    """
    lifecycle = compaction(snapshot, reference)
    if not lifecycle.finished:
        return None
    finishes = [
        entry
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and entry.cursor > reference.started_cursor
        and isinstance(entry.body, CompactionFinishedBodyResponse)
    ]
    assert len(finishes) == 1, f"compaction {name!r} has {len(finishes)} finished feed entries"
    return True


def has_context(
    snapshot: SessionSnapshot,
    reference: CompactionRef,
    name: str,
) -> bool | None:
    """Check that the compaction has non-empty context.

    Returns:
        True after the check, or None before the finished entry arrives.

    """
    finishes = [
        entry.body
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and entry.cursor > reference.started_cursor
        and isinstance(entry.body, CompactionFinishedBodyResponse)
    ]
    if not finishes:
        return None
    assert len(finishes) == 1
    context = finishes[0].context
    assert context is not None, f"compaction {name!r} has no compacted context"
    assert context.text.strip(), f"compaction {name!r} has empty compacted context"
    return True


def has_no_context(
    snapshot: SessionSnapshot,
    reference: CompactionRef,
    name: str,
) -> bool | None:
    """Check that the compaction has no context.

    Returns:
        True after the check, or None before the finished entry arrives.

    """
    finishes = [
        entry.body
        for entry in snapshot.entries
        if entry.actor_id == reference.actor_id
        and entry.cursor > reference.started_cursor
        and isinstance(entry.body, CompactionFinishedBodyResponse)
    ]
    if not finishes:
        return None
    assert len(finishes) == 1
    assert finishes[0].context is None, f"compaction {name!r} unexpectedly has expandable context"
    return True
