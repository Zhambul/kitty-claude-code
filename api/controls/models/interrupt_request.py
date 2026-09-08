# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the interrupt request module."""

# The interrupt gesture.
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    Interrupt,
)


class InterruptRequest(ControlRequestBody):
    """Represent interrupt request."""

    def request(self, session_id: SessionId) -> Interrupt:
        """Return the request.

        Returns:
            Request.

        """
        return Interrupt(session_id, RequestId(self.request_id))
