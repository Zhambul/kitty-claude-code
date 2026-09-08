# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from pathlib import Path

from repository.impl.sqlite.databases import main_database
from repository.impl.sqlite.schema import MAIN_SCHEMA_VERSION
from tests.automatic_naming_job_helpers import remove_naming_schema
from tests.automatic_naming_values import MAIN_DATABASE_NAME


def test_version_thirteen_database_gains_naming(tmp_path: Path) -> None:
    """Verify version thirteen database gains the naming queue."""
    path = str(tmp_path / MAIN_DATABASE_NAME)
    remove_naming_schema(path)

    upgraded = main_database(path)
    upgraded.initialize()
    with upgraded.read() as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='naming_jobs'",
        ).fetchone()
        version = connection.execute(
            "SELECT version FROM schema_version WHERE id=1",
        ).fetchone()

    assert table is not None
    assert version is not None
    assert version["version"] == MAIN_SCHEMA_VERSION
