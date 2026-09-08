# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide repository dependencies."""

from repository.errors import EventIdentityConflictError as EventIdentityConflictError
from repository.impl.sqlite.canonical_events import SqliteCanonicalEventRepository as SqliteCanonicalEventRepository
from repository.impl.sqlite.connection import SqliteDatabase as SqliteDatabase
from repository.impl.sqlite.databases import main_database as main_database
from repository.impl.sqlite.raw_event_audits import SqliteRawEventAuditRepository as SqliteRawEventAuditRepository
from repository.impl.sqlite.raw_events import SqliteRawEventRepository as SqliteRawEventRepository
from repository.impl.sqlite.session_data import SqliteSessionDataRepository as SqliteSessionDataRepository
from repository.impl.sqlite.sessions import SqliteSessionRepository as SqliteSessionRepository
from repository.impl.sqlite.shell_output import SqliteShellOutputRepository as SqliteShellOutputRepository
from repository.mapper import facts as _mapper
from tests import canonical_foundation_components as _foundation_components

mapper = _mapper
foundation_components = _foundation_components
