# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide sqlite repository dependencies."""

from domain import work_state as work_state
from harness.models import raw_events as _raw_event_models
from harness.models.session import Session as Session
from repository import errors as _repository_errors
from repository.contract.session_data import SessionDataChanges as SessionDataChanges
from repository.impl.sqlite import databases as _sqlite_databases, preferences as _sqlite_preferences
from repository.impl.sqlite.canonical_events import SqliteCanonicalEventRepository as SqliteCanonicalEventRepository
from repository.impl.sqlite.connection import SqliteDatabase as SqliteDatabase
from repository.impl.sqlite.raw_event_audits import SqliteRawEventAuditRepository as SqliteRawEventAuditRepository

raw_event_models = _raw_event_models
repository_errors = _repository_errors
sqlite_databases = _sqlite_databases
sqlite_preferences = _sqlite_preferences
