# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from threading import Event

from domain import (
    ids as domain_ids,
    naming as naming_models,
)
from harness.models import controls as control_models
from naming.audit import NamingAudit
from repository.impl.sqlite.naming import SqliteNamingJobRepository
from tests.automatic_naming_job_helpers import (
    assert_failed_naming_job,
    assert_job_enqueued_once,
    unavailable_naming_worker,
)
from tests.automatic_naming_models_one import AppliedTitleRecorder, Audit, FixedModels, RawEvents
from tests.automatic_naming_namer_helper import namer
from tests.automatic_naming_session_helper import session
from tests.automatic_naming_values import SESSION_ID

EXPLICIT_MODEL_REQUESTS = 2


def test_each_explicit_request_generates_fresh(naming_jobs: SqliteNamingJobRepository) -> None:
    """Verify each explicit request generates fresh then retries idempotently."""
    models = FixedModels(("First explicit session title", "Second explicit session title"))
    service = namer(
        models,
        naming_jobs,
        RawEvents(),
    )
    applied_titles: list[str] = []
    record_title = AppliedTitleRecorder(
        applied_titles,
        domain_ids.RequestId("ignored"),
    )

    outcomes = (
        service.requested_name(session(), domain_ids.RequestId("one"), record_title),
        service.requested_name(session(), domain_ids.RequestId("two"), record_title),
        service.requested_name(session(), domain_ids.RequestId("one"), record_title),
    )

    assert all(outcome.status == control_models.ControlAcknowledgement.ACKNOWLEDGED for outcome in outcomes)
    assert len(models.prompts) == EXPLICIT_MODEL_REQUESTS
    assert applied_titles == [
        "First explicit session title",
        "Second explicit session title",
        "First explicit session title",
    ]
    assert "Implement automatic concise naming" in models.prompts[0].prompt


def test_explicit_failure_keeps_current_title(naming_jobs: SqliteNamingJobRepository) -> None:
    """Verify explicit failure keeps the current title unchanged."""
    jobs = naming_jobs
    audit = Audit()
    applied_titles: list[str] = []

    outcome = namer(
        FixedModels(unavailable=True),
        jobs,
        RawEvents(),
        audit=audit,
    ).requested_name(
        session(),
        domain_ids.RequestId("failed"),
        AppliedTitleRecorder(applied_titles, domain_ids.RequestId("failed")),
    )

    assert (outcome.status, outcome.reason) == (
        control_models.ControlAcknowledgement.INDETERMINATE,
        "no small model is currently available",
    )
    assert not applied_titles
    stored = jobs.find(f"requested:{SESSION_ID}:failed")
    assert stored is not None
    assert stored.state == naming_models.NamingJobState.FAILED
    assert audit.errors == [
        (
            str(SESSION_ID),
            "automatic naming (requested)",
            NamingAudit(
                job_key=f"requested:{SESSION_ID}:failed",
                error_type="ModelUnavailableError",
                error="unavailable",
            ),
        ),
    ]


def test_initial_unavailability_marks_job_failed(naming_jobs: SqliteNamingJobRepository) -> None:
    """Verify initial unavailability marks the job failed without an application error."""
    jobs = naming_jobs
    job = naming_models.NamingJob(f"initial:{SESSION_ID}", SESSION_ID, "Name this session")
    assert jobs.enqueue(job)
    audit = Audit()

    assert unavailable_naming_worker(jobs, audit).tick()

    assert_failed_naming_job(jobs, job.key, audit, "failed")


def test_stopping_app_cancels_naming(naming_jobs: SqliteNamingJobRepository) -> None:
    """Verify stopping the application cancels naming without an error."""
    jobs = naming_jobs
    job = naming_models.NamingJob(f"initial:{SESSION_ID}", SESSION_ID, "Name this session")
    assert jobs.enqueue(job)
    audit = Audit()

    stop = Event()
    stop.set()
    assert unavailable_naming_worker(jobs, audit).tick(stop)

    assert_failed_naming_job(jobs, job.key, audit, "cancelled")


def test_job_completion_is_durable(naming_jobs: SqliteNamingJobRepository) -> None:
    """Verify job completion is durable."""
    repository = naming_jobs
    job = naming_models.NamingJob("initial:one", SESSION_ID, "prompt")

    assert_job_enqueued_once(repository, job)
    claimed = repository.claim_next()
    assert claimed is not None
    assert claimed.state == naming_models.NamingJobState.RUNNING
    repository.complete(job.key, "Durable generated session title")

    stored = SqliteNamingJobRepository(repository.database).find(job.key)
    assert stored is not None
    assert stored.title == "Durable generated session title"
    assert stored.state == naming_models.NamingJobState.COMPLETED
