# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the browser events request module."""

from collections.abc import Mapping

from pydantic import BaseModel

from api.common.models.fields import RequiredText, Scalar


class BrowserEventBody(BaseModel):
    """Represent browser event body."""

    name: RequiredText
    session_id: str | None = None
    timestamp: int | None = None
    details: Mapping[str, Scalar] = {}


class BrowserEventsRequest(BaseModel):
    """Represent browser events request."""

    client_id: RequiredText
    device_id: RequiredText
    connection: Mapping[str, Scalar] = {}
    events: tuple[BrowserEventBody, ...]
