# Copyright (c) 2026 Zhambyl Yermagambet
"""Map shell-output following rows and models."""

from __future__ import annotations

from domain import ids as domain_ids, shells as shell_models
from repository.model.facts import ShellOutputRow


def shell_output_following(shell_output_row: ShellOutputRow) -> shell_models.ShellOutputFollowing:
    """Return the shell-output following model for a stored row.

    Returns:
        The shell-output following model for a stored row.

    """
    return shell_models.ShellOutputFollowing(
        session_id=domain_ids.SessionId(shell_output_row.session_id),
        shell_id=domain_ids.ShellId(shell_output_row.shell_id),
        harness=domain_ids.HarnessName(shell_output_row.harness),
        actor_id=domain_ids.ActorId(shell_output_row.actor_id),
        parent_actor_id=(
            None if shell_output_row.parent_actor_id is None else domain_ids.ActorId(shell_output_row.parent_actor_id)
        ),
        source_path=shell_output_row.source_path,
        chunk_source_type=shell_output_row.chunk_source_type,
        delete_source=bool(shell_output_row.delete_source),
        initial_size=int(shell_output_row.initial_size),
        initial_modified_at=int(shell_output_row.initial_modified_at),
        wait_for_source_change=bool(shell_output_row.wait_for_source_change),
        until=shell_output_row.until,  # type: ignore[arg-type]
        state=shell_output_row.state,  # type: ignore[arg-type]
        created_at=shell_output_row.created_at,
    )


def shell_output_row(shell_output_following: shell_models.ShellOutputFollowing) -> ShellOutputRow:
    """Return the storage row for a shell-output following model.

    Returns:
        The storage row for a shell-output following model.

    """
    return ShellOutputRow(
        session_id=shell_output_following.session_id,
        shell_id=shell_output_following.shell_id,
        harness=shell_output_following.harness,
        actor_id=shell_output_following.actor_id,
        parent_actor_id=shell_output_following.parent_actor_id,
        source_path=shell_output_following.source_path,
        chunk_source_type=shell_output_following.chunk_source_type,
        delete_source=int(shell_output_following.delete_source),
        initial_size=shell_output_following.initial_size,
        initial_modified_at=shell_output_following.initial_modified_at,
        wait_for_source_change=int(shell_output_following.wait_for_source_change),
        until=shell_output_following.until,
        state=shell_output_following.state,
        created_at=shell_output_following.created_at,
    )
