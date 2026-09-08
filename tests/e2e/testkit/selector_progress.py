# Copyright (c) 2026 Zhambyl Yermagambet
"""Select stable task and compaction references."""

from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from tests.e2e.testkit import references as refs
from tests.e2e.testkit.selector_common import _one

if TYPE_CHECKING:
    from sdk.client import SessionWatch
    from sdk.state import SessionSnapshot


def _find_task(snapshot: SessionSnapshot, exact_subject: str) -> refs.TaskRef | None:
    candidates = [
        task_state for task_state in snapshot.session_data.session.tasks if task_state.subject == exact_subject
    ]
    task_state = _one(candidates, f"task with subject {exact_subject!r}")
    if task_state is None:
        return None
    return refs.TaskRef(snapshot.session_reference, task_state.task_id)


def task(
    watch: SessionWatch,
    *,
    exact_subject: str,
    timeout: float,
) -> refs.TaskRef:
    """Find one task with the specified subject.

    Returns:
        The task reference.

    """
    return watch.wait(
        f"one task with subject {exact_subject!r}",
        partial(_find_task, exact_subject=exact_subject),
        timeout=timeout,
    )


def _find_compaction(snapshot: SessionSnapshot, after_cursor: int) -> refs.CompactionRef | None:
    candidates = [
        compaction_state
        for compaction_state in snapshot.compactions()
        if compaction_state.started_cursor > after_cursor
    ]
    compaction_state = _one(candidates, "compaction after the named control")
    if compaction_state is None:
        return None
    return refs.CompactionRef(
        snapshot.session_reference,
        compaction_state.actor_id,
        compaction_state.started_cursor,
    )


def compaction(
    watch: SessionWatch,
    *,
    after_cursor: int,
    timeout: float,
) -> refs.CompactionRef:
    """Find one compaction after a cursor.

    Returns:
        The compaction reference.

    """
    return watch.wait(
        "one compaction after the named control",
        partial(_find_compaction, after_cursor=after_cursor),
        timeout=timeout,
    )
