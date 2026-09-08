# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the global application response module."""

# What the list page OWNS: the launch form it half-filled, the directories it
# hid, the notification toggle, the account fuel gauges and the published limits.
#
# No session rows: those are facts the harnesses reported, they live in the read
# model, and they arrive on /sessionData. This is the other half of the page —
# the half nothing but the browser ever wrote.
from collections.abc import Mapping

from pydantic import BaseModel

from api.common.models.values.usage_row import UsageRowResponse
from domain.ids import SessionId


class NotificationNoticeResponse(BaseModel):
    """Represent notification notice response."""

    revision: int
    session_id: SessionId
    kind: str
    project: str
    title: str


class GlobalNotificationStateResponse(BaseModel):
    """Represent global notification state response."""

    enabled: bool
    latest: NotificationNoticeResponse | None


class NewSessionPreferencesResponse(BaseModel):
    """Represent new session preferences response."""

    working_directory: str | None
    harness: str | None
    model: str | None
    effort: str | None


class NewSessionDraftResponse(BaseModel):
    """Represent new session draft response."""

    working_directory: str
    text: str
    sequence: float


class DashboardLimitsResponse(BaseModel):
    """Represent dashboard limits response."""

    upload_bytes: int
    rename_characters: int
    presence_seconds: float


class GlobalPreferencesResponse(BaseModel):
    """Represent global preferences response."""

    new_session: NewSessionPreferencesResponse
    new_session_drafts: tuple[NewSessionDraftResponse, ...]
    hidden_directories: Mapping[str, float]
    limits: DashboardLimitsResponse


class GlobalApplicationResponse(BaseModel):
    """Represent global application response."""

    usage_rows: tuple[UsageRowResponse, ...]
    notifications: GlobalNotificationStateResponse
    preferences: GlobalPreferencesResponse
