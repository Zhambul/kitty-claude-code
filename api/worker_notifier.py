# Copyright (c) 2026 Zhambyl Yermagambet
"""Build the notifier that runs as a daemon worker."""

from app import (
    provider_audit_storage as audit_providers,
    provider_notifications as notification_providers,
    provider_preference_storage as preference_providers,
    provider_runtime as runtime_providers,
    provider_session_storage as session_providers,
    provider_terminal as terminal_providers,
)
from app.injection import Instances, resolve
from notify.notifier import Notifier, NotifierDependencies


def notifier(instances: Instances) -> Notifier:
    """Build the notifier from application providers.

    Returns:
        The notifier.

    """
    return Notifier(
        NotifierDependencies(
            session_data_repository=resolve(instances, session_providers.session_data),
            terminal_adapter=resolve(instances, terminal_providers.terminal),
            repository_queries=resolve(instances, runtime_providers.repositories),
            dashboard_notification_state=resolve(instances, notification_providers.dashboard_notification_state),
            notification_setting_repository=resolve(instances, preference_providers.notification_settings),
            push_subscription_repository=resolve(instances, preference_providers.push_subscriptions),
            push_signing_key_repository=resolve(instances, preference_providers.push_signing_keys),
            presence=resolve(instances, notification_providers.presence),
            audit_recorder=resolve(instances, audit_providers.recorder),
            changes=resolve(instances, notification_providers.application_update_state).changes,
        ),
    )
