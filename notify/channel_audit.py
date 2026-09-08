# Copyright (c) 2026 Zhambyl Yermagambet
"""Audit documents for notification channel delivery."""

from __future__ import annotations

from audit.documents import AuditDocument
from domain.ids import SessionId


class WebPushAudit(AuditDocument):
    """Represent one Web Push delivery audit."""

    session_id: SessionId
    kind: str | None
    action: str
    status: int
    ok: bool
    gone: bool
    error: str
    badge: int
    device: str | None
    endpoint: str


class TelegramSendAudit(AuditDocument):
    """Represent one Telegram send audit."""

    session_id: SessionId | None
    kind: str | None
    reason: str | None
    ok: bool
    status: int
    error: str
    retractable: bool
    message_id: int | None


class TelegramRetractionAudit(AuditDocument):
    """Represent one Telegram retraction audit."""

    session_id: SessionId | None
    kind: str | None
    message_id: int | None
    outcome: str
    status: int
    error: str
