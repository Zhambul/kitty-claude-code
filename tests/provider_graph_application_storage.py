# Copyright (c) 2026 Zhambyl Yermagambet
"""Provider graph access to application storage."""

from __future__ import annotations

from typing import TYPE_CHECKING

from dashboard.services.application_updates import ApplicationUpdateState
from repository.impl.sqlite.audit_read import SqliteAuditReadRepository
from repository.impl.sqlite.preferences import (
    SqliteHiddenDirectoryRepository,
    SqliteNewSessionRepository,
    SqlitePushSubscriptionRepository,
)
from tests.provider_graph_context import ProviderGraphContext

if TYPE_CHECKING:
    from repository.contract.audit import AuditReadRepository
    from repository.contract.preferences import (
        HiddenDirectoryRepository,
        NewSessionRepository,
        PushSubscriptionRepository,
    )


class ProviderGraphApplicationStorage(ProviderGraphContext):
    """Provide application state storage access."""

    @property
    def application_update_state(self) -> ApplicationUpdateState:
        """The application update state."""
        return self.provider("application_update_state", ApplicationUpdateState)

    @property
    def audit_reads(self) -> AuditReadRepository:
        """The audit reader."""
        return self.provider("audit_reads", SqliteAuditReadRepository)

    @property
    def hidden_directories(self) -> HiddenDirectoryRepository:
        """The hidden directory repository."""
        return self.provider("hidden_directories", SqliteHiddenDirectoryRepository)

    @property
    def new_sessions(self) -> NewSessionRepository:
        """The new session repository."""
        return self.provider("new_sessions", SqliteNewSessionRepository)

    @property
    def push_subscriptions(self) -> PushSubscriptionRepository:
        """The push subscription repository."""
        return self.provider("push_subscriptions", SqlitePushSubscriptionRepository)
