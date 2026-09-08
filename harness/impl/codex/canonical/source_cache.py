# Copyright (c) 2026 Zhambyl Yermagambet
"""Build and prune cached Codex event sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from domain import ids as domain_ids, messaging
from harness import contract as harness_contract
from harness.impl.codex.canonical import (
    source_catalog,
    source_readers,
    title as native_title,
)

if TYPE_CHECKING:
    from harness.impl.codex import ids_session_types
    from harness.models import session as session_models


@dataclass(frozen=True)
class CodexSessionSources:
    """Contain cached sources for one Codex session."""

    session_id: domain_ids.SessionId
    source_reference: str
    owns_lead_session: bool
    sources: tuple[harness_contract.HarnessRawEventSource, ...]


def codex_session_sources(
    session: session_models.Session,
    title_repository: native_title.CodexThreadTitleRepository,
) -> CodexSessionSources:
    """Build the lead sources for one Codex session.

    Returns:
        The lead sources for one Codex session.

    """
    owns_lead_session = source_catalog.lead_rollout(session.source_reference)
    lead_sources: tuple[harness_contract.HarnessRawEventSource, ...] = ()
    if owns_lead_session:
        lead_sources = (
            source_readers.CodexRolloutRawEventSource(session.source_context),
            source_readers.CodexTitleRawEventSource(
                session.source_context,
                title_repository,
            ),
        )
    return CodexSessionSources(
        session.session_id,
        session.source_reference,
        owns_lead_session,
        lead_sources,
    )


def file_marker(path: str) -> tuple[int, int, int] | None:
    """Return the values that show a rollout file change.

    Returns:
        The values that show a rollout file change.

    """
    try:
        status = Path(path).stat()
    except OSError:
        return None
    return status.st_ino, status.st_mtime_ns, status.st_size


def without_removed_parents(
    parent_by_path: dict[str, ids_session_types.CodexSessionId],
    removed_paths: frozenset[str],
) -> dict[str, ids_session_types.CodexSessionId]:
    """Remove absent rollout paths from the parent cache.

    Returns:
        A new parent mapping without the removed paths.

    """
    return {path: parent for path, parent in parent_by_path.items() if path not in removed_paths}


def without_removed_sources(
    child_sources: dict[
        tuple[domain_ids.SessionId, str, messaging.ActorRole],
        source_readers.CodexRolloutRawEventSource,
    ],
    removed_paths: frozenset[str],
) -> dict[
    tuple[domain_ids.SessionId, str, messaging.ActorRole],
    source_readers.CodexRolloutRawEventSource,
]:
    """Remove absent rollout paths from the child source cache.

    Returns:
        A new source mapping without entries for the removed paths.

    """
    return {
        source_key: source
        for source_key, source in child_sources.items()
        if source_key[1] not in removed_paths
    }
