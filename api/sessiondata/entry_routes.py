# Copyright (c) 2026 Zhambyl Yermagambet
"""Serve session-data entry pages."""

from typing import Annotated

from fastapi import APIRouter, Query

from api.common.models.fields import SessionIdPath
from api.sessiondata import mapper
from api.sessiondata.models.entry import EntryPageResponse
from app.provider_session_storage import SessionDataStore
from domain.ids import SessionId

router = APIRouter()

DEFAULT_ENTRY_LIMIT = 200
MAXIMUM_ENTRY_LIMIT = 1000


@router.get("/sessionData/{session_id}/entries")
def session_entries(
    session_id: SessionIdPath,
    read_model: SessionDataStore,
    at: int | None = None,
    before: int | None = None,
    limit: Annotated[int, Query(ge=1, le=MAXIMUM_ENTRY_LIMIT)] = DEFAULT_ENTRY_LIMIT,
) -> EntryPageResponse:
    """Return one oldest-first entry page.

    Returns:
        The entry page.

    """
    return mapper.entry_page(
        read_model.entries_page(
            SessionId(session_id),
            at=at,
            before=before,
            limit=limit,
        ),
    )
