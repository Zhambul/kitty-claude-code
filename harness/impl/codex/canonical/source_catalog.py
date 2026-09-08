# Copyright (c) 2026 Zhambyl Yermagambet
"""Find and identify Codex rollout files."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

from pydantic import ValidationError

from harness.impl.codex import ids_session_types
from harness.impl.codex.canonical import record_rollout_headers, record_session_meta, record_session_sources

TEXT_ENCODING = "utf-8"
ROLLOUT_NAME = re.compile(r"rollout-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}-(.+)\.jsonl$")


def codex_session_id(path: str) -> ids_session_types.CodexSessionId:
    """Return the Codex session ID from a rollout path.

    Returns:
        The Codex session ID from a rollout path.

    """
    rollout_path = Path(path)
    match = ROLLOUT_NAME.search(rollout_path.name)
    return ids_session_types.CodexSessionId(
        match.group(1) if match else rollout_path.stem,
    )


def session_metadata(path: str) -> record_session_meta.SessionMetaPayload | None:
    """Return validated session metadata from a rollout file.

    Returns:
        Validated session metadata from a rollout file.

    """
    try:
        with Path(path).open(encoding=TEXT_ENCODING) as source:
            for line in islice(source, 5):
                header = record_rollout_headers.RolloutHeader.model_validate_json(line)
                if header.type == "session_meta":
                    return (
                        record_rollout_headers
                        .RolloutDocument[record_session_meta.SessionMetaPayload]
                        .model_validate_json(line)
                        .payload
                    )
    except (OSError, UnicodeDecodeError, ValidationError):
        return None
    return None


def parent_thread_id(
    session_meta_payload: record_session_meta.SessionMetaPayload | None,
) -> str | None:
    """Return the parent thread ID from session metadata.

    Returns:
        The parent thread ID from session metadata.

    """
    if session_meta_payload is None:
        return None
    source = (
        session_meta_payload.source
        if isinstance(session_meta_payload.source, record_session_sources.SessionMetaSource)
        else None
    )
    spawn = None
    if source is not None and source.subagent is not None:
        spawn = source.subagent.thread_spawn
    spawn_parent = None if spawn is None else spawn.parent_thread_id
    parent = spawn_parent or session_meta_payload.parent_thread_id
    return parent.strip() if parent else None


@dataclass(frozen=True)
class DirectorySnapshot:
    """Contain one directory marker and its entries."""

    marker: tuple[int, int]
    entries: tuple[str, ...]


def _directory_marker(directory: str) -> tuple[int, int] | None:
    try:
        status = Path(directory).stat()
    except OSError:
        return None
    return status.st_ino, status.st_mtime_ns


class RolloutCatalog:
    """Find new rollout files without reading every date directory each tick."""

    def __init__(self, configuration_directory: str) -> None:
        """Initialize the rollout catalog."""
        self.configuration_directory = configuration_directory
        self._root = ""
        self._directories: dict[str, DirectorySnapshot] = {}
        self._rollouts: dict[str, DirectorySnapshot] = {}

    def paths(self) -> tuple[str, ...]:
        """Return current rollout paths.

        Returns:
            Current rollout paths.

        """
        root = str(Path(self.configuration_directory) / "sessions")
        if root != self._root:
            self._root = root
            self._directories.clear()
            self._rollouts.clear()
        years = self._subdirectories(root, 4)
        months = tuple(month for year in years for month in self._subdirectories(year, 2))
        days = tuple(day for month in months for day in self._subdirectories(month, 2))
        return tuple(rollout_path for day in days for rollout_path in self._rollout_files(day))

    def _subdirectories(self, directory: str, name_width: int) -> tuple[str, ...]:
        marker = _directory_marker(directory)
        if marker is None:
            return ()
        previous = self._directories.get(directory)
        if previous is not None and previous.marker == marker:
            return previous.entries
        try:
            with os.scandir(directory) as entries:
                found = tuple(
                    sorted(
                        entry.path
                        for entry in entries
                        if len(entry.name) == name_width
                        and entry.name.isdigit()
                        and entry.is_dir(follow_symlinks=False)
                    ),
                )
        except OSError:
            return ()
        self._directories[directory] = DirectorySnapshot(marker, found)
        return found

    def _rollout_files(self, directory: str) -> tuple[str, ...]:
        marker = _directory_marker(directory)
        if marker is None:
            return ()
        previous = self._rollouts.get(directory)
        if previous is not None and previous.marker == marker:
            return previous.entries
        try:
            with os.scandir(directory) as entries:
                found = tuple(
                    sorted(
                        entry.path
                        for entry in entries
                        if ROLLOUT_NAME.search(entry.name) and entry.is_file(follow_symlinks=False)
                    ),
                )
        except OSError:
            return ()
        self._rollouts[directory] = DirectorySnapshot(marker, found)
        return found


def lead_rollout(path: str) -> bool:
    """Return true when a path names a lead rollout.

    Returns:
        True when a path names a lead rollout.

    """
    rollout_path = Path(path).resolve()
    if not rollout_path.is_file() or not ROLLOUT_NAME.search(rollout_path.name):
        return False
    metadata = session_metadata(str(rollout_path))
    if metadata is None:
        return False
    return metadata.thread_source != "subagent" and not metadata.parent_thread_id
