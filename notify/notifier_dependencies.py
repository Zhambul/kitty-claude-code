# Copyright (c) 2026 Zhambyl Yermagambet
"""Define dependencies for notification processing."""

from __future__ import annotations

from dataclasses import dataclass, field

from audit.recorder import AuditRecorder
from core.change_signal import ChangeSignal
from core.repository import RepositoryQueries
from dashboard.services.notices import DashboardNotificationState
from notify.presence import Presence
from repository.contract.preferences import (
    NotificationSettingRepository,
    PushSigningKeyRepository,
    PushSubscriptionRepository,
)
from repository.contract.session_data import SessionDataRepository
from terminal.adapter import TerminalAdapter


@dataclass(frozen=True)
class NotifierDependencies:
    """Contain the services that notification processing uses."""

    session_data_repository: SessionDataRepository
    terminal_adapter: TerminalAdapter
    repository_queries: RepositoryQueries
    dashboard_notification_state: DashboardNotificationState
    notification_setting_repository: NotificationSettingRepository
    push_subscription_repository: PushSubscriptionRepository
    push_signing_key_repository: PushSigningKeyRepository
    presence: Presence
    audit_recorder: AuditRecorder
    changes: ChangeSignal = field(default_factory=ChangeSignal)
