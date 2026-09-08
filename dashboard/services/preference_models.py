# Copyright (c) 2026 Zhambyl Yermagambet
"""Value objects for global dashboard preferences."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from dashboard.services.notices import DashboardNotificationNotice
from domain.ids import DeviceId, HarnessName, SessionId
from harness.models.usage import (
    UsageRow,
)


@dataclass(frozen=True)
class GlobalNotificationState:
    """Represent global notification state."""

    enabled: bool
    latest: DashboardNotificationNotice | None


@dataclass(frozen=True)
class DashboardLimits:
    """Represent dashboard limits."""

    upload_bytes: int
    rename_characters: int
    presence_seconds: float


@dataclass(frozen=True)
class NewSessionPreferences:
    """Represent new session preferences."""

    working_directory: str | None
    harness: HarnessName | None
    model: str | None
    effort: str | None


@dataclass(frozen=True)
class NewSessionDraft:
    """Represent one new-session draft."""

    working_directory: str
    text: str
    sequence: float


@dataclass(frozen=True)
class ApplicationPreferences:
    """Represent all global preferences needed by the list page."""

    new_session: NewSessionPreferences
    new_session_drafts: tuple[NewSessionDraft, ...]
    hidden_directories: Mapping[str, float]
    limits: DashboardLimits
    notifications: GlobalNotificationState
    usage_rows: tuple[UsageRow, ...]


@dataclass(frozen=True)
class BrowserPushSubscription:
    """Represent one browser Push subscription."""

    endpoint: str
    public_key: str
    authentication_secret: str
    device_id: DeviceId
    device_label: str | None


@dataclass(frozen=True)
class BrowserPresence:
    """Represent one browser presence report."""

    device_id: DeviceId
    session_id: SessionId | None
    away: bool
