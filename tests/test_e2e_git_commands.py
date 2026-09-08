# Copyright (c) 2026 Zhambyl Yermagambet
"""Check isolated Git fixture commands and worktree creation."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import Mock

import pytest

from core.repository import RepositoryQueries
from tests.e2e.testkit import git_commands
from tests.e2e.testkit.repository import RepositoryWorkspace

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def git_command(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Replace executable lookup and the Git process call.

    Returns:
        The Git command probe.

    """
    command = Mock()
    monkeypatch.setattr("tests.e2e.testkit.git_commands.shutil.which", lambda _name: "/test/git")
    monkeypatch.setattr("tests.e2e.testkit.git_commands.subprocess.run", command)
    return command


def test_git_uses_resolved_path(tmp_path: Path, git_command: Mock) -> None:
    """Pass fixture arguments to the resolved executable without a shell."""
    git_commands.run(tmp_path, "status", "--porcelain")
    git_command.assert_called_once_with(
        ("/test/git", "-C", str(tmp_path), "status", "--porcelain"),
        check=True,
        capture_output=True,
        text=True,
    )


def test_missing_git_does_not_start_process(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    git_command: Mock,
) -> None:
    """Report a missing executable before a process can start."""
    monkeypatch.setattr("tests.e2e.testkit.git_commands.shutil.which", lambda _name: None)
    with pytest.raises(FileNotFoundError, match="git is not installed"):
        git_commands.run(tmp_path, "status")
    git_command.assert_not_called()


def test_repository_fixture_creates_worktree(tmp_path: Path) -> None:
    """Create a real isolated worktree with the expected clean branch."""
    workspace = RepositoryWorkspace.create(tmp_path)
    status = RepositoryQueries.status(workspace.working_directory)
    assert status is not None
    assert status.branch == workspace.branch
    assert status.worktree == workspace.worktree
    assert not status.dirty
