# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the auto name session request module."""

# The auto-name gesture.
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    AutoNameSession,
)


class AutoNameSessionRequest(ControlRequestBody):
    """Represent auto name session request."""

    def request(self, session_id: SessionId) -> AutoNameSession:
        """Return the request.

        Returns:
            Request.

        """
        return AutoNameSession(session_id, RequestId(self.request_id))
