# Copyright (c) 2026 Zhambyl Yermagambet
"""Find the native Codex title store for one rollout."""

from __future__ import annotations

import re
from pathlib import Path

from harness.impl.codex.canonical.title_values import CodexTitleStoreMarker

TRANSCRIPT_SUFFIX = ".jsonl"
UUID = re.compile(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})")


def state_database(source_reference: str, configuration_directory: str) -> str:
    """Return the newest native state database, if it exists.

    Returns:
        The database path, or an empty string.

    """
    directory = Path(codex_directory(source_reference, configuration_directory))
    best = max(directory.glob("state_*.sqlite"), key=state_database_version, default=None)
    if best is not None:
        return str(best)
    plain = directory / "state.sqlite"
    return str(plain) if plain.is_file() else ""


def codex_directory(source_reference: str, configuration_directory: str) -> str:
    """Return the Codex home that owns a rollout source.

    Returns:
        The resolved Codex home directory.

    """
    current = Path(source_reference).resolve().parent
    while current != current.parent:
        if current.name == "sessions":
            return str(current.parent)
        current = current.parent
    return configuration_directory


def state_database_version(path: Path) -> int:
    """Return the numeric version of a native state database path.

    Returns:
        The state database version.

    """
    match = re.fullmatch(r"state_(\d+)\.sqlite", path.name)
    return int(match.group(1)) if match else 0


def title_store_marker(source_reference: str, configuration_directory: str) -> CodexTitleStoreMarker | None:
    """Return title-store state used to skip unchanged reads.

    Returns:
        The store marker, or ``None`` when the index is unavailable.

    """
    database = state_database(source_reference, configuration_directory)
    database_state = file_marker(database) if database else None
    if database_state is None:
        return None
    return CodexTitleStoreMarker(database, database_state, file_marker(f"{database}-wal"))


def file_marker(path: str) -> tuple[int, int, int] | None:
    """Return a file change marker.

    Returns:
        The marker, or ``None`` when the file does not exist.

    """
    try:
        status = Path(path).stat()
    except OSError:
        return None
    return status.st_ino, status.st_mtime_ns, status.st_size


def thread_uuid(path: str) -> str:
    """Return the rollout thread UUID from its filename.

    Returns:
        The thread UUID, or an empty string.

    """
    match = UUID.search(Path(path).name)
    return match.group(1) if match else ""
