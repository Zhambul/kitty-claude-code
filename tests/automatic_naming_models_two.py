# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from collections import abc as collections_abc

from domain import (
    entries as domain_entries,
    ids as domain_ids,
)
from harness.models import controls as control_models
from harness.models.session import (
    Session,
)
from terminal import adapter as terminal_adapter


class RecordingTitleAdapter:
    """Represent recording title adapter."""

    def __init__(self, result: terminal_adapter.SessionTerminalResult | None = None) -> None:
        """Create an empty title call record."""
        self.calls: list[tuple[domain_ids.SessionId, str]] = []
        self.result = result or terminal_adapter.SessionTerminalResult(succeeded=True)

    def rename_session_tab(
        self,
        session_id: domain_ids.SessionId,
        title: str,
    ) -> terminal_adapter.SessionTerminalResult:
        """Record the requested session title.

        Returns:
            The configured terminal result.

        """
        self.calls.append((session_id, title))
        return self.result


class ControlReadModel:
    """Represent control read model."""

    def __init__(self) -> None:
        """Create empty read-model call records."""
        self.read_sessions: list[domain_ids.SessionId] = []
        self.attention_sessions: list[domain_ids.SessionId] = []

    def read(self, session_id: domain_ids.SessionId) -> None:
        """Return read."""
        self.read_sessions.append(session_id)

    def pending_attention(self, session_id: domain_ids.SessionId) -> tuple[domain_entries.SessionEntry, ...]:
        """Record the attention query.

        Returns:
            An empty tuple of attention entries.

        """
        self.attention_sessions.append(session_id)
        return ()


class Effects:
    """Represent effects."""

    def __init__(self) -> None:
        """Create empty effect records."""
        self.renames: list[control_models.RenameSession] = []
        self.sessions: list[Session] = []

    def session_renamed(self, stored_session: Session, rename_session: control_models.RenameSession) -> None:
        """Process session renamed."""
        self.sessions.append(stored_session)
        self.renames.append(rename_session)


class RecordingNamer:
    """Represent recording namer."""

    def __init__(self) -> None:
        """Create an empty naming request record."""
        self.calls = 0
        self.requests: list[tuple[Session, domain_ids.RequestId]] = []

    def requested_name(
        self,
        stored_session: Session,
        request_id: domain_ids.RequestId,
        apply_title: collections_abc.Callable[[str], control_models.ControlResult],
    ) -> control_models.ControlResult:
        """Record the request and apply a fixed title.

        Returns:
            The result from the title callback.

        """
        self.calls += 1
        self.requests.append((stored_session, request_id))
        return apply_title("Generated generic control title")


class AcknowledgingHandler:
    """Represent acknowledging handler."""

    def __init__(self) -> None:
        """Create empty control call records."""
        self.requests: list[control_models.ControlRequest] = []
        self.contexts: list[control_models.ControlContext] = []

    def __call__(
        self,
        control_request: control_models.ControlRequest,
        control_context: control_models.ControlContext,
    ) -> control_models.ControlResult:
        """Record and acknowledge the control request.

        Returns:
            A durable title result for rename requests, or a control result.

        """
        self.requests.append(control_request)
        self.contexts.append(control_context)
        if isinstance(control_request, control_models.RenameSession):
            return control_models.DurableTitleResult(
                control_request.request_id,
                control_models.ControlAcknowledgement.ACKNOWLEDGED,
            )
        return control_models.ControlResult(
            control_request.request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
        )
