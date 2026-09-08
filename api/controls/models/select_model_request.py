# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the select model request module."""

# The model-selection gesture.
from api.common.models.fields import RequiredText
from api.controls.models.control_request import ControlRequestBody
from domain.ids import RequestId, SessionId
from harness.models.controls import (
    SelectModel,
)


class SelectModelRequest(ControlRequestBody):
    """Represent select model request."""

    model_id: RequiredText

    def request(self, session_id: SessionId) -> SelectModel:
        """Return the request.

        Returns:
            Request.

        """
        return SelectModel(session_id, RequestId(self.request_id), model=self.model_id)
