# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the background request module."""

# The background gesture: move the running command out of the foreground.
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    Background,
)


class BackgroundRequest(ControlRequestBody):
    """Represent background request."""

    def request(self, session_id: SessionId) -> Background:
        """Return the request.

        Returns:
            Request.

        """
        return Background(session_id, RequestId(self.request_id))
