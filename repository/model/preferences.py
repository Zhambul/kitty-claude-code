# Copyright (c) 2026 Zhambyl Yermagambet
"""Row shapes for the nine preference tables that replaced one `kv` table."""

from __future__ import annotations

from dataclasses import dataclass

from domain.ids import DeviceId, HarnessName, SessionId


@dataclass(frozen=True)
class SessionViewModeRow:
    """Represent session view mode row."""

    session_id: SessionId
    view_mode: str


@dataclass(frozen=True)
class HiddenDirectoryRow:
    """Represent hidden directory row."""

    working_directory: str
    hidden_at: float


@dataclass(frozen=True)
class NewSessionPreferenceRow:
    """Represent new session preference row."""

    id: int
    working_directory: str | None
    harness: HarnessName | None
    model: str | None
    effort: str | None


@dataclass(frozen=True)
class NewSessionDraftRow:
    """Represent new session draft row."""

    working_directory: str
    text: str
    sequence: float


@dataclass(frozen=True)
class PushSubscriptionRow:
    """Represent push subscription row."""

    endpoint: str
    public_key: str
    authentication_secret: str
    device_id: DeviceId
    device_label: str | None
    created_at: float


@dataclass(frozen=True)
class PushSigningKeyRow:
    """Represent push signing key row."""

    id: int
    private_key_pem: str
    public_key: str
