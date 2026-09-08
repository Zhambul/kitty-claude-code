# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide sqlite test dependencies."""

from repository.impl.sqlite.raw_events import SqliteRawEventRepository as SqliteRawEventRepository
from repository.impl.sqlite.schema import MAIN_SCHEMA_VERSION as MAIN_SCHEMA_VERSION
from repository.impl.sqlite.session_data import SqliteSessionDataRepository as SqliteSessionDataRepository
from repository.impl.sqlite.sessions import SqliteSessionRepository as SqliteSessionRepository
from repository.impl.sqlite.shell_output import SqliteShellOutputRepository as SqliteShellOutputRepository
from repository.impl.sqlite.terminal import SqlitePaneWidthRepository as SqlitePaneWidthRepository
from repository.impl.sqlite.uploads import SqliteUploadRepository as SqliteUploadRepository
from repository.impl.sqlite.workspace import SqliteSessionWorkspaceRepository as SqliteSessionWorkspaceRepository
from repository.mapper import documents as documents
