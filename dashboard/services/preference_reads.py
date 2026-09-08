# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide application preference read operations."""

from core.daemon import contract as daemon_contract
from dashboard import config
from dashboard.services import preference_models
from dashboard.services.preference_context import ApplicationPreferenceContext
from notify import presence


class ApplicationPreferenceReadOperations:
    """Provide application preference read operations."""

    def snapshot(self: ApplicationPreferenceContext) -> preference_models.ApplicationPreferences:
        """Return the application preference snapshot.

        Returns:
            The application preference snapshot.

        """
        new_session = self.settings.new_session_repository.preferences()
        hidden_directories = {
            entry.working_directory: entry.hidden_at for entry in self.settings.hidden_directory_repository.hidden()
        }
        return preference_models.ApplicationPreferences(
            new_session=preference_models.NewSessionPreferences(
                working_directory=new_session.working_directory if new_session else None,
                harness=new_session.harness if new_session else None,
                model=new_session.model if new_session else None,
                effort=new_session.effort if new_session else None,
            ),
            new_session_drafts=tuple(
                preference_models.NewSessionDraft(
                    working_directory=draft.working_directory,
                    text=draft.text,
                    sequence=draft.sequence,
                )
                for draft in self.settings.new_session_repository.drafts()
            ),
            hidden_directories=hidden_directories,
            limits=preference_models.DashboardLimits(
                upload_bytes=daemon_contract.UPLOAD_MAX,
                rename_characters=config.RENAME_CHARACTER_LIMIT,
                presence_seconds=presence.VIEW_LIFETIME_SECONDS,
            ),
            notifications=preference_models.GlobalNotificationState(
                enabled=self.settings.notification_setting_repository.alerting_enabled(),
                latest=self.settings.notification_state.notification(),
            ),
            usage_rows=self.core.usage_state.usage_rows(),
        )
