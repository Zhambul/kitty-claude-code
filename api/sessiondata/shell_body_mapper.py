# Copyright (c) 2026 Zhambyl Yermagambet
"""Map shell entry bodies to API responses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.common.mapper import values
from api.sessiondata.models import entry as entry_models
from domain import entry_shells as shell_bodies

if TYPE_CHECKING:
    from domain import entry_base


def map_body(entry_body: entry_base.EntryBody) -> entry_models.EntryBodyResponse | None:
    """Return the API response for a shell entry body.

    Returns:
        The API response for a shell entry body.

    """
    if isinstance(entry_body, shell_bodies.ShellStartedBody):
        return entry_models.ShellStartedBodyResponse(
            shell_id=str(entry_body.shell_id),
            command=values.content(entry_body.command),
            execution=entry_body.execution,
        )
    if isinstance(entry_body, shell_bodies.ShellOutputBody):
        return entry_models.ShellOutputBodyResponse(
            shell_id=str(entry_body.shell_id),
            stream=entry_body.stream,
            mode=entry_body.mode,
            content=values.content(entry_body.content),
        )
    if isinstance(entry_body, shell_bodies.ShellBackgroundedBody):
        return entry_models.ShellBackgroundedBodyResponse(shell_id=str(entry_body.shell_id))
    if isinstance(entry_body, shell_bodies.ShellFinishedBody):
        return entry_models.ShellFinishedBodyResponse(
            shell_id=str(entry_body.shell_id),
            state=entry_body.state,
            exit_code=entry_body.exit_code,
            result=values.maybe_content(entry_body.result),
        )
    return None
