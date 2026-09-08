# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the launch response module."""

# What a launch did. `rejected` carries the same body as `started` — a refusal
# here is a verdict, not an error — and the status is which one it was.
from pydantic import BaseModel

from harness.models.launch import (
    LaunchStatus,
)


class LaunchResponse(BaseModel):
    """Represent launch response."""

    status: LaunchStatus
    window_id: str | None
    reason: str | None
    working_directory: str | None = None
