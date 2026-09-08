# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the select effort request module."""

# The effort-selection gesture.
from api.common.models.fields import RequiredText
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    SelectEffort,
)


class SelectEffortRequest(ControlRequestBody):
    """Represent select effort request."""

    effort: RequiredText

    def request(self, session_id: SessionId) -> SelectEffort:
        """Return the request.

        Returns:
            Request.

        """
        return SelectEffort(session_id, RequestId(self.request_id), effort=self.effort)
