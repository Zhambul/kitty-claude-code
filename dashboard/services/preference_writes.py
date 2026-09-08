# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide application preference write operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain.preferences import NewSessionDraft, NewSessionPreferences, PushSubscription

if TYPE_CHECKING:
    from collections.abc import Mapping

    from dashboard.services import preference_models
    from dashboard.services.preference_context import ApplicationPreferenceContext
    from domain.ids import HarnessName, SessionId

NEW_SESSION_DRAFT_LIMIT = 24


def _project_directory(
    application_preference_context: ApplicationPreferenceContext, session_id: SessionId, working_directory: str,
) -> str:
    session = application_preference_context.core.session_repository.find(session_id)
    if session is not None and session.project_directory:
        return session.project_directory
    return application_preference_context.core.repository_queries.project_directory(working_directory)


class ApplicationPreferenceWriteOperations:
    """Provide application preference write operations."""

    def set_notifications_enabled(self: ApplicationPreferenceContext, *, enabled: bool) -> None:
        """Set notification delivery."""
        repository = self.settings.notification_setting_repository
        previous = repository.alerting_enabled()
        repository.set_alerting_enabled(enabled=enabled)
        if enabled != previous:
            self.signals.application_updates.publish()

    def save_new_session_preferences(
        self: ApplicationPreferenceContext,
        working_directory: str | None,
        harness: HarnessName | None,
        model: str | None,
        effort: str | None,
    ) -> None:
        """Save new-session preferences."""
        preferences = NewSessionPreferences(
            working_directory=working_directory or None,
            harness=harness or None,
            model=model or None,
            effort=effort or None,
        )
        repository = self.settings.new_session_repository
        previous = repository.preferences()
        repository.save_preferences(preferences)
        if preferences != previous:
            self.signals.application_updates.publish()

    def save_new_session_draft(
        self: ApplicationPreferenceContext,
        working_directory: str,
        text: str,
        sequence: float,
    ) -> bool:
        """Save a new-session draft.

        Returns:
            True if the draft was accepted, or False if its sequence was stale.

        """
        written = self.settings.new_session_repository.save_draft(
            NewSessionDraft(working_directory, text if text.strip() else "", sequence),
            NEW_SESSION_DRAFT_LIMIT,
        )
        if not written.stale:
            self.signals.application_updates.publish()
        return not written.stale

    def hide_directory(self: ApplicationPreferenceContext, working_directory: str) -> Mapping[str, float]:
        """Hide an inactive project directory.

        Returns:
            All hidden directories mapped to their hide times.

        Raises:
            ValueError: If the directory has an active terminal session.

        """
        live = [
            session_record
            for session_record in self.core.session_data_repository.visible()
            if _project_directory(self, session_record.session.session_id, session_record.session.working_directory)
            == working_directory
            and self.core.terminal_adapter.window_for_session(session_record.session.session_id) is not None
        ]
        if live:
            msg = "cannot hide a directory with an active session"
            raise ValueError(msg)
        self.settings.hidden_directory_repository.hide(working_directory, self.clock())
        self.signals.application_updates.publish()
        return {
            entry.working_directory: entry.hidden_at for entry in self.settings.hidden_directory_repository.hidden()
        }

    def register_push_subscription(
        self: ApplicationPreferenceContext,
        browser_push_subscription: preference_models.BrowserPushSubscription,
    ) -> None:
        """Register the current browser push subscription."""
        repository = self.settings.push_subscription_repository
        for existing in repository.subscriptions():
            if (
                existing.device_id == browser_push_subscription.device_id
                and existing.endpoint != browser_push_subscription.endpoint
            ):
                repository.remove(existing.endpoint)
        repository.upsert(
            PushSubscription(
                endpoint=browser_push_subscription.endpoint,
                public_key=browser_push_subscription.public_key,
                authentication_secret=browser_push_subscription.authentication_secret,
                device_id=browser_push_subscription.device_id,
                device_label=browser_push_subscription.device_label,
                created_at=self.clock(),
            ),
        )

    def report_presence(
        self: ApplicationPreferenceContext,
        browser_presence: preference_models.BrowserPresence,
    ) -> None:
        """Report browser presence."""
        session_id = browser_presence.session_id
        if browser_presence.away:
            self.signals.presence.mark_away(browser_presence.device_id, session_id)
            return
        self.signals.presence.mark_device(browser_presence.device_id)
        if session_id:
            self.signals.presence.mark_viewing(session_id)
