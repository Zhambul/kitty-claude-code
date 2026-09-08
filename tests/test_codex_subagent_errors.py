# Copyright (c) 2026 Zhambyl Yermagambet
"""Check expected read errors and unexpected failures in child rollout parsing."""

from unittest.mock import Mock

import pytest

from harness.impl.codex.canonical import rollout_subagent_body, rollout_subagent_metadata


@pytest.mark.parametrize("error_type", [OSError, ValueError, OverflowError])
def test_fork_time_handles_invalid_input(monkeypatch: pytest.MonkeyPatch, error_type: type[Exception]) -> None:
    """Treat unavailable files and invalid timestamps as missing fork metadata."""
    reader = Mock(side_effect=error_type("invalid metadata"))
    monkeypatch.setattr(rollout_subagent_metadata, "read_subagent_fork_epoch", reader)

    assert rollout_subagent_metadata.subagent_fork_epoch("rollout.jsonl") is None


def test_fork_time_preserves_code_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not hide an unexpected metadata reader failure."""
    reader = Mock(side_effect=RuntimeError("reader defect"))
    monkeypatch.setattr(rollout_subagent_metadata, "read_subagent_fork_epoch", reader)

    with pytest.raises(RuntimeError, match="reader defect"):
        rollout_subagent_metadata.subagent_fork_epoch("rollout.jsonl")


def test_child_boundary_handles_invalid_input(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip a line that fails native record validation."""
    parser = Mock(side_effect=ValueError("invalid record"))
    monkeypatch.setattr(rollout_subagent_body, "parse_line", parser)

    assert not rollout_subagent_body.is_child_bootstrap_line(b"invalid", 0)


def test_child_boundary_preserves_code_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Do not hide an undeclared record kind or another parser defect."""
    parser = Mock(side_effect=RuntimeError("parser defect"))
    monkeypatch.setattr(rollout_subagent_body, "parse_line", parser)

    with pytest.raises(RuntimeError, match="parser defect"):
        rollout_subagent_body.is_child_bootstrap_line(b"invalid", 0)
