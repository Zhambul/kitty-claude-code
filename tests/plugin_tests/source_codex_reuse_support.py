# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for Codex source reuse tests."""

import json
from dataclasses import dataclass
from functools import partial
from pathlib import Path

import pytest

from domain import (
    ids as domain_ids,
)
from harness.impl.codex.canonical import source_catalog, source_readers, sources
from harness.models.session import (
    Session,
)
from tests.plugin_tests import vocabulary as fixture
from tests.plugin_tests.source_catalog_support import record_catalog_paths
from tests.plugin_tests.source_codex_native_support import rollout_path


def write_codex_lead_rollout(tmp_path: Path) -> Path:
    """Write a Codex rollout header for a lead session.

    Returns:
        The path of the new rollout file.

    """
    lead_path = rollout_path(tmp_path, "24", "rollout-2026-08-24T10-00-00-lead-one.jsonl")
    lead_path.parent.mkdir(parents=True)
    lead_path.write_text(
        json.dumps(
            {
                fixture.TYPE_FIELD: fixture.SESSION_META_ID,
                fixture.PAYLOAD_FIELD: {
                    fixture.ID_FIELD: fixture.LEAD_ONE_ID,
                    fixture.CWD_FIELD: fixture.WORK_PATH,
                    fixture.THREAD_SOURCE: fixture.USER,
                },
            },
        )
        + "\n",
    )
    return lead_path


@dataclass(frozen=True)
class CodexSourceReuseFixture:
    """Hold a session, source factory, and catalog query record."""

    session: Session
    factory: sources.CodexRawEventSources
    catalog_invocations: list[None]


def codex_source_reuse_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> CodexSourceReuseFixture:
    """Build a source factory that records catalog queries.

    Returns:
        The lead session, factory, and shared query record.

    """
    lead_path = write_codex_lead_rollout(tmp_path)
    session = Session(
        domain_ids.SessionId(fixture.LEAD_ONE_ID),
        domain_ids.ActorId("lead-one:lead"),
        str(lead_path),
        fixture.WORK_PATH,
    )
    catalog = source_catalog.RolloutCatalog(tmp_path.as_posix())
    catalog_invocations: list[None] = []
    monkeypatch.setattr(
        catalog,
        "paths",
        partial(record_catalog_paths, catalog_invocations, catalog.paths),
    )
    monkeypatch.setattr(source_catalog, "RolloutCatalog", lambda _directory: catalog)
    return CodexSourceReuseFixture(session, sources.CodexRawEventSources(tmp_path.as_posix()), catalog_invocations)


def rotated_source_actors(
    factory: sources.CodexRawEventSources,
    session: Session,
) -> list[domain_ids.ActorId]:
    """Check that each source is a rollout and read its actor identity.

    Returns:
        The actor identities in source order.

    """
    actors = []
    for source in factory.for_session(session):
        assert isinstance(source, source_readers.CodexRolloutRawEventSource)
        actors.append(source.context.actor_id)
    return actors
