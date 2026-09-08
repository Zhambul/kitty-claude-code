# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http contract dependencies."""

from harness.models.session import Session as Session
from harness.services import controls as _control_services, open_session_work as open_session_work
from harness.services.terminal_gate import SessionTerminalGate as SessionTerminalGate
from notify.presence import Presence as Presence
from repository.impl.sqlite.raw_event_audits import SqliteRawEventAuditRepository as SqliteRawEventAuditRepository
from terminal.panes.commands import PaneCommandOutcome as PaneCommandOutcome
from tests import canonical_runtime as canonical_runtime, fake_terminal as fake_terminal

control_services = _control_services
