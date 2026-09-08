# Copyright (c) 2026 Zhambyl Yermagambet
"""Connect session-data event routes to their services."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from fastapi.responses import StreamingResponse

from api.common.models.fields import SessionIdPath
from api.sessiondata import stream_dependencies
from api.sessiondata.stream_global_frames import global_frames
from api.sessiondata.stream_global_models import GlobalFrameSources
from api.sessiondata.stream_session_frames import session_frames
from api.sessiondata.stream_session_models import SessionStreamServices
from api.sse import EVENT_STREAM, NO_STORE
from domain.ids import SessionId

router = APIRouter()


SessionStreamDependency = Annotated[
    SessionStreamServices,
    Depends(stream_dependencies.session_stream_services),
]

GlobalStreamDependency = Annotated[
    GlobalFrameSources,
    Depends(stream_dependencies.global_stream_sources),
]


def from_cursor(last_event_id: str | None, after_cursor: int) -> int:
    """Return the client resume cursor, or the query cursor when it is absent.

    Returns:
        The client resume cursor, or the query cursor when it is absent.

    """
    if last_event_id is None:
        return after_cursor
    try:
        return int(last_event_id)
    except ValueError:
        return after_cursor


@router.get("/sessionData/{session_id}/stream")
def session_stream(
    session_id: SessionIdPath,
    services: SessionStreamDependency,
    after_cursor: int = 0,
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    *,
    include_application: bool = True,
) -> StreamingResponse:
    """Return the session stream response.

    Returns:
        The session stream response.

    """
    return StreamingResponse(
        session_frames(
            services,
            SessionId(session_id),
            from_cursor(last_event_id, after_cursor),
            include_application=include_application,
        ),
        media_type=EVENT_STREAM,
        headers=NO_STORE,
    )


@router.get("/sessionData/stream")
def global_stream(
    sources: GlobalStreamDependency,
    after_cursor: int = 0,
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
) -> StreamingResponse:
    """Return the global stream response.

    Returns:
        The global stream response.

    """
    return StreamingResponse(
        global_frames(sources, from_cursor(last_event_id, after_cursor)),
        media_type=EVENT_STREAM,
        headers=NO_STORE,
    )
