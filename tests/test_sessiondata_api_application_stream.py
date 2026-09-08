# Copyright (c) 2026 Zhambyl Yermagambet
"""Test sessiondata api application stream."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import pytest

from dashboard.services.application_updates import ApplicationUpdateState
from tests import (
    canonical_sessiondata_api_frame_parsing as frame_parsing,
    canonical_sessiondata_api_stream_changes as stream_changes,
    canonical_sessiondata_api_stream_models as stream_models,
)

if TYPE_CHECKING:

    from repository.impl.sqlite.session_data import SqliteSessionDataRepository

EXPECTED_APPLICATION_READS = 2


@pytest.mark.usefixtures("tmp_path")
def test_global_stream_reads_app_state_only(session_data_store: SqliteSessionDataRepository) -> None:
    """Verify the global stream reads application state only after a revision."""
    application = stream_models.ApplicationSnapshots()
    updates = ApplicationUpdateState()

    initial, changed, stable_reads = asyncio.run(
        stream_changes.read_changed_application_frame(session_data_store, application, updates),
    )

    assert frame_parsing.frame_body(initial)["notifications"]["enabled"] is True
    assert frame_parsing.frame_body(changed)["notifications"]["enabled"] is False
    assert "id:" not in changed
    assert stable_reads == 1
    assert application.reads == EXPECTED_APPLICATION_READS
