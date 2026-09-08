# Copyright (c) 2026 Zhambyl Yermagambet
"""Group the dependencies of automatic session naming."""

from __future__ import annotations

from dataclasses import dataclass

from audit.recorder import AuditRecorder
from inference.contract import ModelFactory
from repository.contract.facts import RawEventRepository
from repository.contract.naming import NamingJobRepository
from repository.contract.session_data import SessionDataRepository


@dataclass(frozen=True)
class AutomaticNamingResources:
    """Hold the services that automatic naming needs."""

    model_factory: ModelFactory
    naming_job_repository: NamingJobRepository
    raw_event_repository: RawEventRepository
    session_data_repository: SessionDataRepository
    audit_recorder: AuditRecorder
