# Copyright (c) 2026 Zhambyl Yermagambet
"""Run durable automatic naming jobs in the background."""

from __future__ import annotations

from contextlib import ExitStack
from typing import TYPE_CHECKING

from core.change_signal import ChangeSignal
from inference.errors import ModelUnavailableError
from naming.audit import NamingAudit, record_job_state

if TYPE_CHECKING:
    import threading

    from audit.recorder import AuditRecorder
    from domain.naming import NamingJob
    from harness.models.session import (
        Session,
    )
    from naming.service import AutomaticSessionNamer
    from repository.contract import naming, sessions

NAMING_RETRY_SECONDS = 1.0
MODEL_UNAVAILABLE_REASON = "no small model is currently available"
APPLICATION_STOPPED_REASON = "application stopped"


class NamingJobWorker:
    """Claim and run durable automatic naming jobs."""

    def __init__(
        self,
        naming_job_repository: naming.NamingJobRepository,
        session_repository: sessions.SessionRepository,
        automatic_session_namer: AutomaticSessionNamer,
        audit_recorder: AuditRecorder,
        *,
        changes: ChangeSignal | None = None,
    ) -> None:
        """Create a worker with naming and storage dependencies."""
        self.jobs = naming_job_repository
        self.sessions = session_repository
        self.namer = automatic_session_namer
        self.audit = audit_recorder
        self.changes = ChangeSignal() if changes is None else changes
        self._wake: threading.Event | None = None

    def run(self, stop_event: threading.Event) -> None:
        """Drain stored jobs, then wait for a change notice."""
        with ExitStack() as cleanup, self.changes.subscribe_thread() as changed:
            self._wake = changed
            cleanup.callback(setattr, self, "_wake", None)
            while not stop_event.is_set():
                changed.clear()
                delay = _drain_jobs(self, stop_event)
                if stop_event.is_set():
                    return
                changed.wait(delay)

    def stop(self) -> None:
        """Release the worker wait after its stop event is set."""
        if self._wake is not None:
            self._wake.set()

    def tick(self, stop_event: threading.Event | None = None) -> bool:
        """Return the tick.

        Returns:
            Tick.

        """
        job = self.jobs.claim_next()
        if job is None:
            return False
        session = self.sessions.find(job.session_id)
        if session is None:
            self.jobs.fail(job.key, "session is unavailable")
            return True
        try:
            self._complete_job(job, session)
        except ModelUnavailableError:
            self._record_unavailable(job, session, cancelled=stop_event is not None and stop_event.is_set())
        except Exception as error:  # noqa: BLE001 — the raised-path assertion
            self._record_unexpected(job, session, error)
        return True

    def _complete_job(self, job: NamingJob, session: Session) -> None:
        title = self.namer.initial_name(session, job.prompt)
        self.jobs.complete(job.key, title)
        record_job_state(self.audit, job.key, str(session.session_id), "completed", title)

    def _record_unavailable(self, job: NamingJob, session: Session, *, cancelled: bool) -> None:
        reason = APPLICATION_STOPPED_REASON if cancelled else MODEL_UNAVAILABLE_REASON
        status = "cancelled" if cancelled else "failed"
        self.jobs.fail(job.key, reason)
        record_job_state(self.audit, job.key, str(session.session_id), status)

    def _record_unexpected(self, job: NamingJob, session: Session, error: Exception) -> None:
        self.audit.error(
            str(session.session_id),
            "automatic naming (initial)",
            NamingAudit(
                job_key=job.key,
                error_type=type(error).__name__,
                error=str(error),
            ),
        )
        self.jobs.fail(job.key, MODEL_UNAVAILABLE_REASON)
        record_job_state(self.audit, job.key, str(session.session_id), "failed")


def _drain_jobs(worker: NamingJobWorker, stop_event: threading.Event) -> float | None:
    try:
        while not stop_event.is_set():
            if not worker.tick(stop_event):
                return None
    except Exception:  # noqa: BLE001 -- Record failed jobs and keep the worker available.
        worker.audit.error("", "automatic naming worker")
        return NAMING_RETRY_SECONDS
    return None
