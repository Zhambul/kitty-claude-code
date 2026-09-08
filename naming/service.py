# Copyright (c) 2026 Zhambyl Yermagambet
"""Generate, validate, and apply concise session titles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from domain import naming as naming_domain
from harness.models.controls import ControlAcknowledgement, ControlResult
from inference.errors import ModelUnavailableError
from naming import audit as naming_audit, generator, observations, session_prompt

if TYPE_CHECKING:
    from collections.abc import Callable

    from domain.ids import RequestId
    from harness.models.session import Session
    from naming.resources import AutomaticNamingResources

MODEL_UNAVAILABLE_REASON = "no small model is currently available"
GENERATION_FAILURE_REASON = "automatic title generation failed"
AUTOMATIC_TITLE_ACTION = "automatic_title"


class AutomaticSessionNamer:
    """Generate and store automatic names for one session."""

    def __init__(
        self,
        resources: AutomaticNamingResources,
    ) -> None:
        """Create a namer with model and storage dependencies."""
        self.generator = generator.TitleGenerator(resources.model_factory)
        self.jobs = resources.naming_job_repository
        self.title_observations = observations.AutomaticTitleRecorder(resources.raw_event_repository)
        self.read_model = resources.session_data_repository
        self.audit = resources.audit_recorder

    def initial_name(self, session: Session, first_prompt: str) -> str:
        """Generate and record the initial automatic session name.

        Returns:
            Text result.

        """
        title = self.generator.generate(first_prompt, str(session.session_id))
        key = f"initial:{session.session_id}"
        self.title_observations.record(session, key, title)
        return title

    def requested_name(
        self,
        session: Session,
        request_id: RequestId,
        apply_title: Callable[[str], ControlResult],
    ) -> ControlResult:
        """Generate and apply one requested automatic session name.

        Returns:
            The control result.

        """
        key = f"requested:{session.session_id}:{request_id}"
        job, inserted = self.jobs.register_running(
            naming_domain.NamingJob(
                key,
                session.session_id,
                "",
                naming_domain.NamingJobState.RUNNING,
            ),
        )
        if not inserted:
            if job.state == naming_domain.NamingJobState.COMPLETED and job.title:
                return apply_title(job.title)
            return _existing_request_result(request_id, job.state)
        try:
            outcome = self._apply_generated_name(session, key, apply_title)
        except ModelUnavailableError as error:
            self._record_failure(session, key, error, MODEL_UNAVAILABLE_REASON)
            return _failure_result(request_id, MODEL_UNAVAILABLE_REASON)
        except Exception as error:  # noqa: BLE001 — the raised-path assertion
            self._record_failure(session, key, error, GENERATION_FAILURE_REASON)
            return _failure_result(request_id, GENERATION_FAILURE_REASON)
        else:
            return outcome

    def _apply_generated_name(
        self,
        session: Session,
        job_key: str,
        apply_title: Callable[[str], ControlResult],
    ) -> ControlResult:
        prompt = session_prompt.first_user_prompt(session, self.read_model)
        title = self.generator.generate(prompt, str(session.session_id))
        self.jobs.complete(job_key, title)
        outcome = apply_title(title)
        self.audit.state_file(
            str(session.session_id),
            "",
            AUTOMATIC_TITLE_ACTION,
            naming_audit.NamingAudit(job_key=job_key, title=title, status=outcome.status),
        )
        return outcome

    def _record_failure(
        self,
        session: Session,
        job_key: str,
        error: Exception,
        reason: str,
    ) -> None:
        self.audit.error(
            str(session.session_id),
            "automatic naming (requested)",
            naming_audit.NamingAudit(
                job_key=job_key,
                error_type=type(error).__name__,
                error=str(error),
            ),
        )
        self.jobs.fail(job_key, reason)
        self._audit_failure(session, job_key)

    def _audit_failure(self, session: Session, key: str) -> None:
        self.audit.state_file(
            str(session.session_id),
            "",
            AUTOMATIC_TITLE_ACTION,
            naming_audit.NamingAudit(job_key=key, status="failed"),
        )


def _existing_request_result(
    request_id: RequestId,
    state: naming_domain.NamingJobState,
) -> ControlResult:
    reason = (
        "automatic naming request is already in progress"
        if state == naming_domain.NamingJobState.RUNNING
        else MODEL_UNAVAILABLE_REASON
    )
    return ControlResult(
        request_id,
        ControlAcknowledgement.INDETERMINATE,
        reason,
    )


def _failure_result(request_id: RequestId, reason: str) -> ControlResult:
    return ControlResult(
        request_id,
        ControlAcknowledgement.INDETERMINATE,
        reason,
    )
