# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the compact request module."""

# The compact gesture.
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    Compact,
)


class CompactRequest(ControlRequestBody):
    """Represent compact request."""

    def request(self, session_id: SessionId) -> Compact:
        """Return the request.

        Returns:
            Request.

        """
        return Compact(session_id, RequestId(self.request_id))
