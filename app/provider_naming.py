# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide automatic session naming services."""

from typing import Annotated

from fastapi import Depends

from app import (
    provider_audit_storage as audit_providers,
    provider_auxiliary_storage as storage_providers,
    provider_fact_storage as fact_providers,
    provider_harness_sessions as session_providers,
    provider_inference as inference_providers,
    provider_notifications as notification_providers,
    provider_session_storage as session_data_providers,
)
from app.injection import singleton
from naming import jobs, resources, service


@singleton
def automatic_namer(
    models: inference_providers.InferenceModels,
    naming_jobs: storage_providers.NamingJobs,
    raw: fact_providers.RawEvents,
    read_model: session_data_providers.SessionDataStore,
    audit: audit_providers.Recorder,
) -> service.AutomaticSessionNamer:
    """Return the automatic session naming service.

    Returns:
        Automatic session naming service.

    """
    return service.AutomaticSessionNamer(
        resources.AutomaticNamingResources(
            models,
            naming_jobs,
            raw,
            read_model,
            audit,
        ),
    )


AutomaticNamer = Annotated[
    service.AutomaticSessionNamer,
    Depends(automatic_namer),
]


@singleton
def naming_worker(
    naming_jobs: storage_providers.NamingJobs,
    session_storage: session_providers.Sessions,
    namer: AutomaticNamer,
    audit: audit_providers.Recorder,
    updates: notification_providers.ApplicationUpdates,
) -> jobs.NamingJobWorker:
    """Return the durable automatic naming worker.

    Returns:
        Durable automatic naming worker.

    """
    return jobs.NamingJobWorker(
        naming_jobs,
        session_storage,
        namer,
        audit,
        changes=updates.changes,
    )
