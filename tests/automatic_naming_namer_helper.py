# Copyright (c) 2026 Zhambyl Yermagambet
"""Durable jobs, title safety, and generic naming semantics."""

from __future__ import annotations

import typing

from naming.resources import AutomaticNamingResources
from naming.service import AutomaticSessionNamer

if typing.TYPE_CHECKING:
    from audit.recorder import AuditRecorder
    from inference import contract as inference_contract
    from repository.contract.facts import RawEventRepository
    from repository.contract.session_data import SessionDataRepository
    from repository.impl.sqlite.naming import SqliteNamingJobRepository

from tests.automatic_naming_models_one import Audit, FixedModels, RawEvents, ReadModel


def namer(
    model_factory: FixedModels,
    jobs: SqliteNamingJobRepository,
    raw_events: RawEvents,
    prompt: str = "Implement automatic concise naming",
    audit: Audit | None = None,
) -> AutomaticSessionNamer:
    """Build a naming service with test dependencies.

    Returns:
        The naming service with the supplied model and job store.

    """
    return AutomaticSessionNamer(
        AutomaticNamingResources(
            typing.cast("inference_contract.ModelFactory", model_factory),
            jobs,
            typing.cast("RawEventRepository", raw_events),
            typing.cast("SessionDataRepository", ReadModel(prompt)),
            typing.cast("AuditRecorder", audit or Audit()),
        ),
    )
