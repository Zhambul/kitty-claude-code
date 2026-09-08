# Copyright (c) 2026 Zhambyl Yermagambet
"""Parse the stable porcelain form of Git status output."""

from __future__ import annotations

from dataclasses import dataclass

HEAD_PREFIX = "# branch.head "
REVISION_PREFIX = "# branch.oid "
DETACHED_HEAD = "(detached)"
UNKNOWN_REVISION = "?"
SHORT_REVISION_LENGTH = 7


@dataclass(frozen=True)
class RepositoryStatus:
    """Describe the current branch and worktree state."""

    branch: str
    worktree: str | None
    dirty: bool


def parse_status(output: str) -> tuple[str, bool]:
    """Return the branch name and dirty state from Git status output.

    Returns:
        Branch name and dirty state from Git status output.

    """
    lines = output.splitlines()
    return _branch_name(lines), _has_changes(lines)


def _branch_name(lines: list[str]) -> str:
    head = _metadata_value(lines, HEAD_PREFIX)
    if head and head != DETACHED_HEAD:
        return head
    revision = _metadata_value(lines, REVISION_PREFIX) or UNKNOWN_REVISION
    return revision[:SHORT_REVISION_LENGTH]


def _metadata_value(lines: list[str], prefix: str) -> str | None:
    for line in lines:
        if line.startswith(prefix):
            return line.removeprefix(prefix)
    return None


def _has_changes(lines: list[str]) -> bool:
    return any(line and not line.startswith("# ") for line in lines)
