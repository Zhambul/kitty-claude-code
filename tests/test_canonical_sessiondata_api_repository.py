# Copyright (c) 2026 Zhambyl Yermagambet
"""Test canonical sessiondata api repository."""

from __future__ import annotations

import subprocess  # noqa: S404 -- Use CompletedProcess as the result of a mocked Git query.
from typing import TYPE_CHECKING
from unittest.mock import Mock

from core.git_status import RepositoryStatus
from core.repository import RepositoryQueries
from tests import canonical_sessiondata_api_git as git_support

if TYPE_CHECKING:
    from pathlib import Path

    import pytest


def test_repo_identity_maps_linked_worktree(tmp_path: Path) -> None:
    """Verify repository identity maps a linked worktree to its main checkout."""
    source = tmp_path / "project"
    linked = tmp_path / "project-worktree"
    git_support.create_linked_worktree(source, linked)

    status = RepositoryQueries.status(str(linked))
    project_directory = RepositoryQueries.project_directory(str(linked))

    assert status is not None
    assert status.branch == "worktree"
    assert status.dirty is False
    assert status.worktree == linked.name
    assert project_directory == str(source)


def test_repo_status_uses_one_git_query(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify repository status uses one git query and handles detached head."""
    run_git = Mock(
        return_value=subprocess.CompletedProcess(
            (),
            0,
            "# branch.oid 1234567890abcdef\n# branch.head (detached)\n? untracked.txt\n",
            "",
        ),
    )
    monkeypatch.setattr(RepositoryQueries, "run_git", run_git)

    status = RepositoryQueries.status("/not-a-worktree")

    assert status == RepositoryStatus(branch="1234567", worktree=None, dirty=True)
    run_git.assert_called_once_with(
        "/not-a-worktree",
        "status",
        "--porcelain=v2",
        "--branch",
    )
