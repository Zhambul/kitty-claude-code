# Copyright (c) 2026 Zhambyl Yermagambet
"""Apply provider selection and retry policy for the small model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from inference.audit import ModelUnavailableAudit, ProviderAttemptAudit, error_context
from inference.errors import ModelUnavailableError, ProviderUnavailableError
from inference.retry import ProviderAttemptQueue

if TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from inference.commands import ProviderCandidate
    from inference.contract import ModelPromptRequest, ModelPromptResponse
    from inference.providers import CandidateSelection, ProviderSelector
    from inference.runner import ModelRunner


class SmallModel:
    """Send one prompt through the best available small model provider."""

    def __init__(
        self,
        provider_selector: ProviderSelector,
        model_runner: ModelRunner,
        audit_recorder: AuditRecorder,
    ) -> None:
        """Create a model with selection, execution, and audit services."""
        self.selector = provider_selector
        self.runner = model_runner
        self.audit = audit_recorder

    def send(self, model_prompt_request: ModelPromptRequest) -> ModelPromptResponse:
        """Send one prompt with bounded provider fallback.

        Returns:
            The model prompt response.

        """
        try:
            selection = self.selector.select()
        except Exception as error:
            self.audit.error(
                model_prompt_request.session_id,
                "small model (provider selection)",
                error_context(error),
            )
            raise
        return self._send_selected(selection, model_prompt_request)

    def _send_selected(
        self,
        selection: CandidateSelection,
        request: ModelPromptRequest,
    ) -> ModelPromptResponse:
        failures: list[str] = []
        attempts = ProviderAttemptQueue(selection.candidates)
        while attempts:
            candidate = attempts.take()
            try:
                return self.runner.send(candidate, request)
            except ProviderUnavailableError as error:
                failures.append(f"{candidate.harness}: {error}")
                attempts.retry(candidate, error)
            except Exception as error:
                self._audit_unexpected(request, candidate, attempts.attempt, error)
                raise
        return self._raise_unavailable(request, selection, failures)

    def _audit_unexpected(
        self,
        request: ModelPromptRequest,
        candidate: ProviderCandidate,
        attempt: int,
        error: Exception,
    ) -> None:
        audit_document = error_context(error)
        self.audit.error(
            request.session_id,
            "small model (provider attempt)",
            ProviderAttemptAudit(
                error_type=audit_document.error_type,
                error=audit_document.error,
                provider=candidate.harness,
                attempt=attempt,
            ),
        )

    def _raise_unavailable(
        self,
        request: ModelPromptRequest,
        selection: CandidateSelection,
        failures: list[str],
    ) -> ModelPromptResponse:
        reason = "; ".join(failures) if failures else "no provider is available"
        error = ModelUnavailableError(reason)
        audit_document = error_context(error)
        self.audit.error(
            request.session_id,
            "small model (unavailable)",
            ModelUnavailableAudit(
                error_type=audit_document.error_type,
                error=audit_document.error,
                providers=selection.provider_states,
                attempt_failures=tuple(failures),
            ),
        )
        raise error
