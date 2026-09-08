# Copyright (c) 2026 Zhambyl Yermagambet
"""Map lifecycle entry bodies to API responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.mapper import values
from api.sessiondata.models import entry as entry_models
from domain import entry_lifecycle as lifecycle_bodies

if TYPE_CHECKING:
    from domain import entry_base


def map_body(entry_body: entry_base.EntryBody) -> entry_models.EntryBodyResponse | None:
    """Return the API response for a lifecycle entry body.

    Returns:
        The API response for a lifecycle entry body.

    """
    if isinstance(entry_body, lifecycle_bodies.CompactionStartedBody):
        return entry_models.CompactionStartedBodyResponse(before_tokens=entry_body.before_tokens)
    if isinstance(entry_body, lifecycle_bodies.CompactionFinishedBody):
        return entry_models.CompactionFinishedBodyResponse(
            before_tokens=entry_body.before_tokens,
            after_tokens=entry_body.after_tokens,
            context=values.maybe_content(entry_body.context),
        )
    if isinstance(entry_body, lifecycle_bodies.AssignmentStartedBody):
        return entry_models.AssignmentStartedBodyResponse(
            assignment_id=str(entry_body.assignment_id),
            assigned_actor_name=entry_body.assigned_actor_name,
            prompt=values.maybe_content(entry_body.prompt),
        )
    if isinstance(entry_body, lifecycle_bodies.AssignmentFinishedBody):
        return entry_models.AssignmentFinishedBodyResponse(
            assignment_id=str(entry_body.assignment_id),
            state=entry_body.state,
            result=values.maybe_content(entry_body.result),
        )
    if isinstance(entry_body, lifecycle_bodies.ModelChangeBody):
        response: entry_models.EntryBodyResponse | None = entry_models.ModelChangeBodyResponse(
            current=entry_body.current, previous=entry_body.previous, automatic=entry_body.automatic,
        )
    elif isinstance(entry_body, lifecycle_bodies.EffortChangeBody):
        response = entry_models.EffortChangeBodyResponse(current=entry_body.current, previous=entry_body.previous)
    else:
        response = None
    return response
