# Copyright (c) 2026 Zhambyl Yermagambet
"""Find the child-owned part of a Codex subagent rollout."""

from __future__ import annotations

from pathlib import Path

from harness.impl.codex.canonical import record_task_records, record_terminal_records
from harness.impl.codex.canonical.rollout_parsing import parse_line
from harness.impl.codex.canonical.rollout_subagent_metadata import subagent_fork_epoch


def is_child_bootstrap(rec: record_terminal_records.RolloutRecord | None, fork_epoch: int | None) -> bool:
    """Return whether a record starts the child-owned rollout body.

    Returns:
        Whether a record starts the child-owned rollout body.

    """
    if fork_epoch is None or not isinstance(rec, record_task_records.TaskStartedRecord):
        return False
    at = rec.at or 0
    return isinstance(at, (int, float)) and at >= fork_epoch


def subagent_body_offset(path: str) -> int:
    """Return the offset of the first child-owned record, or zero.

    Returns:
        The offset of the first child-owned record, or zero.

    """
    fork_epoch = subagent_fork_epoch(path)
    if fork_epoch is None:
        return 0
    try:
        return find_child_body_offset(path, fork_epoch)
    except OSError:
        return 0


def find_child_body_offset(path: str, fork_epoch: int) -> int:
    """Find the child-owned boundary in a rollout file.

    Returns:
        The byte offset of the first child start, or zero if none is found.

    """
    body_offset = 0
    with Path(path).open("rb") as rollout_file:
        for raw_line in rollout_file:
            if is_child_bootstrap_line(raw_line, fork_epoch):
                return body_offset
            body_offset += len(raw_line)
    return 0


def is_child_bootstrap_line(raw_line: bytes, fork_epoch: int) -> bool:
    """Return whether one raw line starts the child-owned rollout body.

    Returns:
        Whether one raw line starts the child-owned rollout body.

    """
    try:
        record = parse_line(raw_line.decode("utf-8", "replace"))
    except ValueError:
        return False
    return is_child_bootstrap(record, fork_epoch)
