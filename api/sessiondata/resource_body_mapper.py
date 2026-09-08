# Copyright (c) 2026 Zhambyl Yermagambet
"""Map resource entry bodies to API responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.mapper import values
from api.sessiondata.models import entry as entry_models
from domain import entry_resources as resource_bodies

if TYPE_CHECKING:
    from domain import entry_base


def map_body(entry_body: entry_base.EntryBody) -> entry_models.EntryBodyResponse | None:
    """Return the API response for a resource entry body.

    Returns:
        The API response for a resource entry body.

    """
    if isinstance(entry_body, resource_bodies.FileBody):
        return entry_models.FileBodyResponse(
            path=entry_body.path,
            action=entry_body.action,
            state=entry_body.state,
            previous_path=entry_body.previous_path,
            line_start=entry_body.line_start,
            line_end=entry_body.line_end,
            lines_added=entry_body.lines_added,
            lines_removed=entry_body.lines_removed,
            content=values.maybe_content(entry_body.content),
        )
    if isinstance(entry_body, resource_bodies.SearchBody):
        return entry_models.SearchBodyResponse(
            tool=entry_body.tool,
            query=values.content(entry_body.query),
            state=entry_body.state,
            result=values.maybe_content(entry_body.result),
        )
    if isinstance(entry_body, resource_bodies.WebBody):
        return entry_models.WebBodyResponse(
            url=entry_body.url, state=entry_body.state, result=values.maybe_content(entry_body.result),
        )
    if isinstance(entry_body, resource_bodies.BrowserBody):
        return entry_models.BrowserBodyResponse(
            action=entry_body.action, state=entry_body.state, result=values.maybe_content(entry_body.result),
        )
    if isinstance(entry_body, resource_bodies.WorktreeBody):
        response: entry_models.EntryBodyResponse | None = entry_models.WorktreeBodyResponse(
            action=entry_body.action, state=entry_body.state, arguments=values.maybe_content(entry_body.arguments),
        )
    else:
        response = None
    return response
