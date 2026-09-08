# Copyright (c) 2026 Zhambyl Yermagambet
"""Named worktree-change acquisition and checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from api.sessiondata.models.entry import WorktreeBodyResponse
from tests.e2e.testkit import selector_changes

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from sdk.state import SessionSnapshot
    from tests.e2e.testkit.observation_contexts import WorkObservationContext
    from tests.e2e.testkit.references import (
        Sessions,
        WorktreeChangeRef,
        WorktreeChanges,
    )
    from tests.e2e.testkit.repository import RepositoryWorkspace


def _change(
    snapshot: SessionSnapshot,
    reference: WorktreeChangeRef,
) -> WorktreeBodyResponse:
    found = [
        entry.body
        for entry in snapshot.entries
        if entry.entry_id == reference.entry_id and isinstance(entry.body, WorktreeBodyResponse)
    ]
    if len(found) != 1:
        message = f"worktree change {reference.entry_id!r} has {len(found)} matches"
        raise AssertionError(
            message,
        )
    return found[0]


@when(
    parsers.parse(
        'I name the {action} worktree change in work "{work_name}" "{change_name}"',
    ),
)
def name_worktree_change(
    worktree_observation_context: WorkObservationContext[WorktreeChangeRef],
    action: str,
    work_name: str,
    change_name: str,
) -> None:
    """Process name worktree change."""
    work = worktree_observation_context.works.get(work_name)
    worktree_observation_context.references.bind(
        change_name,
        selector_changes.worktree_change(
            worktree_observation_context.client.sessions.watch(work.session),
            turn_reference=work.turn,
            action=action,
            timeout=worktree_observation_context.wait_policy.feed,
        ),
    )


@then(parsers.parse('worktree change "{name}" has state {state}'))
def worktree_change_has_state(
    client: BaqylauClient,
    worktree_changes: WorktreeChanges,
    name: str,
    state: str,
) -> None:
    """Process worktree change has state."""
    reference = worktree_changes.get(name)
    assert _change(client.sessions.snapshot(reference.session), reference).state == state


@then(
    parsers.parse(
        'session "{session_name}" reports the exact {state} isolated repository state',
    ),
)
def session_reports_repository_state(
    client: BaqylauClient,
    sessions: Sessions,
    repository_workspace: RepositoryWorkspace,
    session_name: str,
    state: str,
) -> None:
    """Check the reported branch, worktree, and dirty state.

    Raises:
        AssertionError: If the requested state is neither clean nor dirty.

    """
    if state not in {"clean", "dirty"}:
        message = f"unknown repository state {state!r}"
        raise AssertionError(message)
    repository = client.sessions.snapshot(sessions.get(session_name)).session_data.repository
    assert repository is not None
    assert repository.branch == repository_workspace.branch
    assert repository.worktree == repository_workspace.worktree
    assert repository.dirty is (state == "dirty")


@when("I remove the isolated linked worktree")
def remove_isolated_linked_worktree(
    repository_workspace: RepositoryWorkspace,
) -> None:
    """Remove isolated linked worktree."""
    repository_workspace.remove_linked_worktree()
