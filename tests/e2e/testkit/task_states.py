# Copyright (c) 2026 Zhambyl Yermagambet
"""Read task state from session snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from api.sessiondata.models.session_data import TaskResponse
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.references import TaskRef


def task(snapshot: SessionSnapshot, reference: TaskRef) -> TaskResponse:
    """Return state for one task reference.

    Returns:
        The matching task state.

    Raises:
        AssertionError: If the snapshot does not have one matching task.

    """
    found = [
        task_state for task_state in snapshot.session_data.session.tasks if task_state.task_id == reference.task_id
    ]
    if len(found) != 1:
        message = f"task {reference.task_id!r} has {len(found)} matches"
        raise AssertionError(message)
    return found[0]
