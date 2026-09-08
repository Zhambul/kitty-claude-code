# Copyright (c) 2026 Zhambyl Yermagambet
"""Test sessiondata api failed stream."""

from __future__ import annotations

import asyncio

from tests import (
    canonical_sessiondata_api_frame_parsing as frame_parsing,
    canonical_sessiondata_api_stream_changes as stream_changes,
    canonical_sessiondata_api_stream_models as stream_models,
)


def test_stream_that_fails_says_so_and_ends_so() -> None:
    """Verify a stream that fails says so and ends so the client reconnects.

    An SSE stream drives a whole view; dying silently would leave a page
        frozen with no way to know it.
    """
    audit = stream_models.SilentAudit()
    frame = asyncio.run(stream_changes.read_failed_session_frame(audit))
    assert frame_parsing.frame_body(frame) == {"error": "stream failed"}
    assert [where for where, _context in audit.failures] == ["session data stream"]
