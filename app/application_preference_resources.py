# Copyright (c) 2026 Zhambyl Yermagambet
"""Group dependencies for global application preferences."""

from dataclasses import dataclass

from core.repository import RepositoryQueries
from dashboard.services.application_updates import ApplicationUpdateState
from dashboard.services.notices import DashboardNotificationState
from harness.services.usage import ApplicationUsageState
from notify.presence import Presence
from repository.contract import preferences
from repository.contract.session_data import SessionDataRepository
from repository.contract.sessions import SessionRepository
from terminal.adapter import TerminalAdapter


@dataclass(frozen=True)
class ApplicationPreferenceCore:
    """Hold live session and usage preference dependencies."""

    session_data_repository: SessionDataRepository
    session_repository: SessionRepository
    terminal_adapter: TerminalAdapter
    repository_queries: RepositoryQueries
    usage_state: ApplicationUsageState


@dataclass(frozen=True)
class ApplicationPreferenceSettings:
    """Hold stored application preference dependencies."""

    notification_state: DashboardNotificationState
    new_session_repository: preferences.NewSessionRepository
    notification_setting_repository: preferences.NotificationSettingRepository
    hidden_directory_repository: preferences.HiddenDirectoryRepository
    push_subscription_repository: preferences.PushSubscriptionRepository


@dataclass(frozen=True)
class ApplicationPreferenceSignals:
    """Hold live presence and update signals."""

    presence: Presence
    application_updates: ApplicationUpdateState
