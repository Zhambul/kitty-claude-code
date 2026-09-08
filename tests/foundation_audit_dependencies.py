# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide audit dependencies."""

from app.raw_events_audit_cli import main as _raw_event_audit_main
from audit.documents import AuditContent as AuditContent
from audit.failures import FailureContext as FailureContext
from audit.recorder import AuditRecorder as AuditRecorder

raw_event_audit_main = _raw_event_audit_main
