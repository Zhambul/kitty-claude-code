# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the close session request module."""

# The close-session gesture.
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    CloseSession,
)


class CloseSessionRequest(ControlRequestBody):
    """Represent close session request."""

    def request(self, session_id: SessionId) -> CloseSession:
        """Return the request.

        Returns:
            Request.

        """
        return CloseSession(session_id, RequestId(self.request_id))
