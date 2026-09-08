# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

from http import HTTPStatus

from sdk import application_models, control_models, transport, wait_states
from sdk.client_adapters import (
    LAUNCH,
    LAUNCH_TIMEOUT_SECONDS,
    SESSION_LIST,
)
from sdk.client_models import (
    LaunchRef,
    SessionLaunchRequest,
    SessionRef,
)
from sdk.client_wait import wait_for


class _SessionsResourceState:
    """Store session resource transport state."""

    def __init__(self, transport: transport.HttpTransport) -> None:
        """Initialize the sessions resource."""
        self.transport = transport


class _SessionsLaunches(_SessionsResourceState):
    """Launch sessions and find their first state."""

    def list(self) -> application_models.session_data.SessionDataListResponse:
        """Return list.

        Returns:
            List.

        """
        return self.transport.get("/sessionData", SESSION_LIST)

    def launch(
        self,
        request: SessionLaunchRequest,
    ) -> LaunchRef:
        """Launch launch.

        Returns:
            The launch ref.

        Raises:
            ApiFailureError: If the API request fails.

        """
        known = frozenset(session_summary.session.session_id for session_summary in self.list().sessions)
        status, answer = self.transport.post(
            "/api/sessions",
            control_models.launch_session_request.LaunchSessionRequest(
                harness=request.harness,
                working_directory=request.workspace,
                initial_text=request.prompt,
                model_id=request.model,
                effort=request.effort,
                account_id=request.account_id,
                resume_session_id=request.resume_session_id,
                attachments=request.attachments,
            ),
            LAUNCH,
            {HTTPStatus.ACCEPTED, HTTPStatus.CONFLICT},
            timeout=LAUNCH_TIMEOUT_SECONDS,
        )
        if status != HTTPStatus.ACCEPTED or answer.window_id is None:
            rejection_reason = answer.reason or answer.status
            msg = f"session launch was rejected: {rejection_reason}"
            raise transport.ApiFailureError(msg)
        return LaunchRef(request.harness, request.workspace, str(answer.window_id), known)

    def wait_for_session(self, launch: LaunchRef, timeout: float = 120.0) -> SessionRef:
        """Wait for session.

        Returns:
            The session ref.

        """
        session_candidates = wait_states.SessionCandidates()
        return wait_for(
            lambda: (
                f"launch window {launch.window_id!r} to announce one session; found {session_candidates.session_ids}"
            ),
            lambda: self._find_announced_session(launch, session_candidates),
            timeout=timeout,
        )

    def _find_announced_session(
        self,
        launch: LaunchRef,
        session_candidates: wait_states.SessionCandidates,
    ) -> SessionRef | None:
        session_candidates.session_ids = [
            session_summary.session.session_id
            for session_summary in self.list().sessions
            if session_summary.session.session_id not in launch.known_session_ids
            and session_summary.session.harness == launch.harness
            and session_summary.session.working_directory == launch.workspace
        ]
        if len(session_candidates.session_ids) > 1:
            message = f"launch window {launch.window_id!r} has multiple new sessions: {session_candidates.session_ids}"
            raise AssertionError(message)
        if not session_candidates.session_ids:
            return None
        return SessionRef(session_candidates.session_ids[0])
