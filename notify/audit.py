# Copyright (c) 2026 Zhambyl Yermagambet
"""Closed audit documents for notification work."""

from __future__ import annotations

from audit.documents import AuditDocument
from domain.ids import SessionId


class NotificationSessionAudit(AuditDocument):
    """Represent notification session audit."""

    session_id: SessionId | None


class NotificationSuppressedAudit(AuditDocument):
    """Represent notification suppressed audit."""

    session_id: SessionId
    kind: str
    reason: str


class NotificationRouteCandidateAudit(AuditDocument):
    """Represent notification route candidate audit."""

    device: str
    label: str | None
    age_s: float | None


class NotificationRouteAudit(AuditDocument):
    """Represent notification route audit."""

    target: str | None
    target_label: str | None
    subscription_count: int
    candidates: tuple[NotificationRouteCandidateAudit, ...]
    session_id: SessionId
    kind: str


class NotificationRetractionAudit(AuditDocument):
    """Represent notification retraction audit."""

    session_id: SessionId
    channel: str
    kind: str | None
    reason: str
    outcome: str
    age_seconds: float
