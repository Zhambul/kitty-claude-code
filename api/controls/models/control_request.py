# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the control request module."""

# The base every control-gesture request shares: the caller's request id, and
# the one thing every gesture body must be able to do — build the harness
# dataclass that IS the gesture. The route depends on this type, not on each
# subclass, so the promise belongs here rather than in a docstring.
from pydantic import BaseModel

from api.common.models.fields import RequiredText
from domain.ids import SessionId
from harness.models.controls import (
    ControlRequest,
)


class ControlRequestBody(BaseModel):
    """Represent control request body."""

    request_id: RequiredText

    def request(self, session_id: SessionId) -> ControlRequest:
        """Return the request."""
        message = f"{type(self).__name__} builds no control request"
        raise NotImplementedError(message)
