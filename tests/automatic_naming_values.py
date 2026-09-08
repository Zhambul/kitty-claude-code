# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from pathlib import Path

import pytest

from domain import (
    ids as domain_ids,
)
from repository.impl.sqlite.databases import main_database
from repository.impl.sqlite.naming import SqliteNamingJobRepository

SESSION_ID = domain_ids.SessionId("session-one")


TITLE_CHARACTER_LIMIT = 80


ACTOR_ID = domain_ids.ActorId("actor-one")


MAIN_DATABASE_NAME = "main.db"


@pytest.fixture
def naming_jobs(tmp_path: Path) -> SqliteNamingJobRepository:
    """Return the naming job repository for one test database.

    Returns:
        The naming job repository for one test database.

    """
    return SqliteNamingJobRepository(main_database(str(tmp_path / MAIN_DATABASE_NAME)))
