# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata api store."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from repository.impl.sqlite.databases import main_database
from repository.impl.sqlite.session_data import SqliteSessionDataRepository
from tests import canonical_sessiondata_api_values as api_values

if TYPE_CHECKING:
    from pathlib import Path

    from domain import (
        session_state,
    )


@pytest.fixture
def session_data_store(tmp_path: Path) -> SqliteSessionDataRepository:
    """Return an isolated session-data repository.

    Returns:
        An isolated session-data repository.

    """
    return SqliteSessionDataRepository(main_database(str(tmp_path / "main.db")))


def stored_data(read_model: SqliteSessionDataRepository) -> session_state.SessionData:
    """Return the session data that a prior write must create.

    Returns:
        The session data that a prior write must create.

    """
    session_record = read_model.read(api_values.SESSION)
    assert session_record is not None
    return session_record
