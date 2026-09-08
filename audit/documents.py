# Copyright (c) 2026 Zhambyl Yermagambet
"""Small closed documents stored in operational audit rows."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from domain.ids import SessionId


class AuditDocument(BaseModel):
    """Provide strict and immutable fields for an audit document."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class EmptyAudit(AuditDocument):
    """Represent an audit event that needs no additional fields."""


class ShortErrorAudit(AuditDocument):
    """Hold one short error message."""

    error: str


class PathAudit(AuditDocument):
    """Hold one audited file-system path."""

    path: str


class PortAudit(AuditDocument):
    """Hold one audited network port."""

    port: int


class SessionAudit(AuditDocument):
    """Hold an optional audited session identifier."""

    session_id: SessionId | None


type AuditContent = BaseModel | str | None
