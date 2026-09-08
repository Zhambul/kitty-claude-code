# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sdk import application_models, transport
from sdk.client_adapters import (
    SAVED,
    SESSION_APPLICATION,
)
from sdk.client_answers import (
    QuestionAnswer,
    _answer_selection,
)

if TYPE_CHECKING:
    from pydantic import BaseModel

    from sdk.client_application import ApplicationResource
    from sdk.client_models import SessionRef


class _PreferencesState:
    """Store services shared by preference resources."""

    def __init__(self, transport: transport.HttpTransport, application: ApplicationResource) -> None:
        """Initialize the preferences resource."""
        self.transport = transport
        self.application = application

    def _save(self, path: str, document: BaseModel) -> application_models.saved_response.SavedResponse:
        _status, response = self.transport.post(path, document, SAVED, {200})
        return response


class _ApplicationPreferences(_PreferencesState):
    """Read application preference state."""

    def global_state(self) -> application_models.global_application_response.GlobalApplicationResponse:
        """Return the global state.

        Returns:
            Global state.

        """
        return self.application.state()

    def session_state(
        self, session: SessionRef,
    ) -> application_models.session_application_response.SessionApplicationResponse:
        """Return the session state.

        Returns:
            Session state.

        """
        session_id = session.path_segment
        return self.transport.get(
            f"/api/sessions/{session_id}/application",
            SESSION_APPLICATION,
        )


class _NewSessionPreferences(_PreferencesState):
    """Save preferences for a new session."""

    def save_new_session_choices(
        self,
        *,
        workspace: str,
        harness: str,
        model: str,
        effort: str,
    ) -> application_models.saved_response.SavedResponse:
        """Save new session choices.

        Returns:
            The saved response.

        """
        return self._save(
            "/api/application/new-session-preferences",
            application_models.new_session_preferences_request.NewSessionPreferencesRequest(
                working_directory=workspace,
                harness=harness,
                model=model,
                effort=effort,
            ),
        )

    def save_new_session_draft(
        self,
        *,
        workspace: str,
        text: str,
        sequence: float,
    ) -> application_models.saved_response.SavedResponse:
        """Save new session draft.

        Returns:
            The saved response.

        """
        return self._save(
            "/api/application/new-session-drafts",
            application_models.new_session_draft_request.NewSessionDraftRequest(
                working_directory=workspace,
                text=text,
                sequence=sequence,
            ),
        )


class _SessionPreferences(_PreferencesState):
    """Save preferences for one existing session."""

    def save_composer_draft(
        self,
        session: SessionRef,
        *,
        text: str,
        origin: str,
        sequence: float,
    ) -> application_models.saved_response.SavedResponse:
        """Save composer draft.

        Returns:
            The saved response.

        """
        session_id = session.path_segment
        return self._save(
            f"/api/sessions/{session_id}/application/composer-draft",
            application_models.composer_draft_request.ComposerDraftRequest(text=text, origin=origin, sequence=sequence),
        )

    def save_question_draft(
        self,
        session: SessionRef,
        *,
        attention_id: str,
        answers: tuple[QuestionAnswer, ...],
        origin: str,
    ) -> application_models.saved_response.SavedResponse:
        """Save question draft.

        Returns:
            The saved response.

        """
        session_id = session.path_segment
        selections = tuple(_answer_selection(answer) for answer in answers)
        return self._save(
            f"/api/sessions/{session_id}/application/dialog-draft",
            application_models.dialog_draft_request.DialogDraftRequest(
                attention_id=attention_id,
                answers=selections,
                origin=origin,
            ),
        )

    def set_view_mode(self, session: SessionRef, view_mode: str) -> application_models.saved_response.SavedResponse:
        """Set view mode.

        Returns:
            The saved response.

        """
        session_id = session.path_segment
        return self._save(
            f"/api/sessions/{session_id}/application/view-mode",
            application_models.view_mode_request.ViewModeRequest(view_mode=view_mode),
        )

    def set_notifications_muted(
        self, session: SessionRef, *, muted: bool,
    ) -> application_models.saved_response.SavedResponse:
        """Set notifications muted.

        Returns:
            The saved response.

        """
        session_id = session.path_segment
        return self._save(
            f"/api/sessions/{session_id}/application/notifications-muted",
            application_models.notifications_muted_request.NotificationsMutedRequest(muted=muted),
        )

    def set_tasks_hidden(self, session: SessionRef, *, hidden: bool) -> application_models.saved_response.SavedResponse:
        """Set tasks hidden.

        Returns:
            The saved response.

        """
        session_id = session.path_segment
        return self._save(
            f"/api/sessions/{session_id}/application/tasks-hidden",
            application_models.tasks_hidden_request.TasksHiddenRequest(hidden=hidden),
        )


class PreferencesResource(
    _ApplicationPreferences,
    _NewSessionPreferences,
    _SessionPreferences,
):
    """Read and save application preferences."""
