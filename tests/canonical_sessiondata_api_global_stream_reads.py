# Copyright (c) 2026 Zhambyl Yermagambet
"""Canonical sessiondata api global stream reads."""

from __future__ import annotations

from typing import TYPE_CHECKING

from api.sessiondata import streams
from dashboard.services.application_updates import ApplicationUpdateState
from tests import canonical_sessiondata_api_stream_models as stream_models

if TYPE_CHECKING:
    from repository.impl.sqlite.session_data import SqliteSessionDataRepository


async def read_global_frames(
    read_model: SqliteSessionDataRepository,
) -> tuple[str, str, str]:
    """Read the initial frames from the global stream.

    Returns:
        The ready, application, and session frames in stream order.

    """
    reader = stream_models.FrameReader(
        streams.global_frames(
            streams.GlobalFrameSources(
                read_model,
                stream_models.SilentAudit(),
                "boot-one",
                stream_models.ApplicationSnapshots(),
                ApplicationUpdateState(),
            ),
            0,
        ),
    )
    ready = await reader.next()
    application_frame = await reader.next()
    session_frame = await reader.next()
    await reader.aclose()
    return ready, application_frame, session_frame
