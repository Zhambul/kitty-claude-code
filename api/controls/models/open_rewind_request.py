# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the open rewind request module."""

# The open-rewind gesture.
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    OpenRewind,
)


class OpenRewindRequest(ControlRequestBody):
    """Represent open rewind request."""

    def request(self, session_id: SessionId) -> OpenRewind:
        """Return the request.

        Returns:
            Request.

        """
        return OpenRewind(session_id, RequestId(self.request_id))
