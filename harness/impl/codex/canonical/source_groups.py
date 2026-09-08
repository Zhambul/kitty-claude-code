# Copyright (c) 2026 Zhambyl Yermagambet
"""Group Codex child rollout paths by their parent session."""

from __future__ import annotations

from dataclasses import dataclass

from harness.impl.codex import ids_session_types


@dataclass
class ChildRollouts:
    """Contain rollout paths for one parent session."""

    parent_session_id: ids_session_types.CodexSessionId
    paths: tuple[str, ...]


@dataclass
class PendingRollout:
    """Contain one rollout that has no readable metadata yet."""

    path: str
    marker: tuple[int, int, int] | None = None


def updated_pending_rollouts(
    pending_rollouts: list[PendingRollout],
    removed_paths: frozenset[str],
    added_paths: frozenset[str],
) -> list[PendingRollout]:
    """Update pending rollout paths after a catalog scan.

    Returns:
        Retained pending entries followed by new entries for added paths.

    """
    updated = [pending for pending in pending_rollouts if pending.path not in removed_paths]
    updated.extend(PendingRollout(path) for path in added_paths)
    return updated


def child_rollout_groups(
    parent_by_path: dict[str, ids_session_types.CodexSessionId],
) -> list[ChildRollouts]:
    """Group all child paths by their parent session.

    Returns:
        Groups sorted by parent identifier, with paths sorted within each group.

    """
    grouped_paths = _paths_by_parent(parent_by_path)
    return [
        ChildRollouts(group_parent_id, tuple(sorted(paths)))
        for group_parent_id, paths in sorted(grouped_paths.items())
    ]


def _paths_by_parent(
    parent_by_path: dict[str, ids_session_types.CodexSessionId],
) -> dict[ids_session_types.CodexSessionId, list[str]]:
    grouped_paths: dict[ids_session_types.CodexSessionId, list[str]] = {}
    for rollout_path, parent_session_id in parent_by_path.items():
        grouped_paths.setdefault(parent_session_id, []).append(rollout_path)
    return grouped_paths
