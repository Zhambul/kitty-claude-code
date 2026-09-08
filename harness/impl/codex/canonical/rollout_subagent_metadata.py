# Copyright (c) 2026 Zhambyl Yermagambet
"""Read the Codex subagent fork time from a rollout head."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from harness.impl.codex.canonical import record_rollout_headers, record_session_meta, record_session_sources


def subagent_fork_epoch(path: str) -> int | None:
    """Return a subagent rollout fork time, or no value for other files.

    Returns:
        A subagent rollout fork time, or no value for other files.

    """
    try:
        return read_subagent_fork_epoch(path)
    except (OSError, ValueError, OverflowError):
        return None


def read_subagent_fork_epoch(path: str) -> int | None:
    """Read a subagent rollout fork time from its first line.

    Returns:
        The fork time in whole Unix seconds, or None if the metadata is not for a subagent.

    """
    line = first_line(path)
    header = record_rollout_headers.RolloutHeader.model_validate_json(line)
    if header.type != "session_meta":
        return None
    document = record_rollout_headers.RolloutDocument[record_session_meta.SessionMetaPayload].model_validate_json(line)
    metadata = document.payload
    if not is_subagent_metadata(metadata):
        return None
    timestamp = metadata.timestamp or document.timestamp or ""
    return int(datetime.fromisoformat(timestamp).timestamp())


def first_line(path: str) -> str:
    """Read the first line from a rollout file.

    Returns:
        The first line including its line ending, or empty text for an empty file.

    """
    with Path(path).open(encoding="utf-8") as source_file:
        return source_file.readline()


def is_subagent_metadata(metadata: record_session_meta.SessionMetaPayload) -> bool:
    """Return whether session metadata describes a subagent thread.

    Returns:
        Whether session metadata describes a subagent thread.

    """
    source = metadata.source if isinstance(metadata.source, record_session_sources.SessionMetaSource) else None
    spawn = source.subagent.thread_spawn if source and source.subagent else None
    return metadata.thread_source == "subagent" or spawn is not None
