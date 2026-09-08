# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

import typing
from collections import abc as collections_abc

from audit.documents import AuditContent
from domain import (
    content as domain_content,
    entries as domain_entries,
    entry_conversation,
    ids as domain_ids,
    messaging,
)
from harness.models import controls as control_models
from harness.models.raw_events import (
    RawEvent,
)
from harness.models.session import (
    Session,
)
from inference import contract as inference_contract
from inference.errors import ModelUnavailableError
from tests.automatic_naming_values import ACTOR_ID, SESSION_ID


class AppliedTitleRecorder:
    """Record titles and acknowledge their application."""

    def __init__(
        self,
        applied_titles: list[str],
        request_id: domain_ids.RequestId,
    ) -> None:
        """Keep the title list and request identity."""
        self._applied_titles = applied_titles
        self._request_id = request_id

    def __call__(self, title: str) -> control_models.DurableTitleResult:
        """Record one title.

        Returns:
            An acknowledged title result for the stored request.

        """
        self._applied_titles.append(title)
        return control_models.DurableTitleResult(
            self._request_id,
            control_models.ControlAcknowledgement.ACKNOWLEDGED,
        )


class FixedModels:
    """Represent fixed models."""

    def __init__(self, responses: tuple[str, ...] = (), *, unavailable: bool = False) -> None:
        """Store fixed model responses."""
        self.responses = list(responses)
        self.unavailable = unavailable
        self.prompts: list[inference_contract.ModelPromptRequest] = []

    def big(self) -> None:
        """Reject use of the large model.

        Raises:
            NotImplementedError: Always; this test factory has only a small model.

        """
        raise NotImplementedError

    def mid(self) -> None:
        """Reject use of the medium model.

        Raises:
            NotImplementedError: Always; this test factory has only a small model.

        """
        raise NotImplementedError

    def small(self) -> inference_contract.Model:
        """Return this test model.

        Returns:
            This model, with its fixed response queue.

        """
        return self

    def send(
        self, model_prompt_request: inference_contract.ModelPromptRequest,
    ) -> inference_contract.ModelPromptResponse:
        """Record the prompt and consume the next fixed response.

        Returns:
            The next response in the queue.

        Raises:
            ModelUnavailableError: If the model is set as unavailable.

        """
        self.prompts.append(model_prompt_request)
        if self.unavailable:
            message = "unavailable"
            raise ModelUnavailableError(message)
        return inference_contract.ModelPromptResponse(self.responses.pop(0))


class RawEvents:
    """Represent raw events."""

    def __init__(self) -> None:
        """Create an empty raw-event recorder."""
        self.events: list[RawEvent] = []

    def record(self, raw_events: collections_abc.Sequence[RawEvent]) -> None:
        """Record record."""
        self.events.extend(raw_events)


class ReadModel:
    """Represent read model."""

    def __init__(self, prompt: str) -> None:
        """Store the prompt for read-model responses."""
        self.prompt = prompt
        self.session_queries: list[domain_ids.SessionId] = []
        self.entry_type_queries: list[tuple[str, ...]] = []

    def entries_of_types(
        self,
        session_id: domain_ids.SessionId,
        entry_types: collections_abc.Sequence[str],
    ) -> tuple[domain_entries.SessionEntry, ...]:
        """Record the query and build the fixed user message.

        Returns:
            One session entry with the configured prompt.

        """
        self.session_queries.append(session_id)
        self.entry_type_queries.append(tuple(entry_types))
        return (
            domain_entries.SessionEntry(
                domain_ids.CanonicalEventId("prompt-event"),
                SESSION_ID,
                ACTOR_ID,
                None,
                None,
                1.0,
                None,
                entry_conversation.MessageBody(
                    domain_ids.MessageId("message-one"),
                    messaging.MessageRole.USER,
                    messaging.MessagePhase.PROMPT,
                    domain_content.TextContent(self.prompt),
                ),
            ),
        )


class Audit:
    """Represent audit."""

    def __init__(self) -> None:
        """Create empty audit records."""
        self.states: list[tuple[str, str, str, AuditContent]] = []
        self.errors: list[tuple[str, str, AuditContent]] = []

    def state_file(
        self,
        log: str,
        path: str,
        action: str,
        content: AuditContent = "",
    ) -> None:
        """Process state file."""
        self.states.append((log, path, action, content))

    def error(
        self,
        session_or_log: str = "",
        func: str = "",
        context: AuditContent = None,
    ) -> None:
        """Process error."""
        self.errors.append((session_or_log, func, context))


class Sessions:
    """Represent sessions."""

    def __init__(self, stored_session: Session) -> None:
        """Store one session fixture."""
        self.stored_session = stored_session

    def find(self, session_id: domain_ids.SessionId) -> Session | None:
        """Return find.

        Returns:
            Find.

        """
        return self.stored_session if self.stored_session.session_id == session_id else None


class Adapter:
    """Represent adapter."""

    def __init__(self) -> None:
        """Create an empty adapter call record."""
        self.sessions: list[domain_ids.SessionId] = []

    def window_for_session(self, session_id: domain_ids.SessionId) -> domain_ids.WindowId | None:
        """Record the session window query.

        Returns:
            None, because this adapter has no terminal windows.

        """
        self.sessions.append(session_id)
        return typing.cast("domain_ids.WindowId | None", None)
