# Copyright (c) 2026 Zhambyl Yermagambet
"""Own config models."""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, ConfigDict

FOREIGN = ConfigDict(extra="forbid", frozen=True, validate_by_name=True)


OPEN_FOREIGN = ConfigDict(extra="ignore", frozen=True, validate_by_name=True)


class ForeignMetadata(BaseModel):
    """Represent foreign metadata."""

    model_config = OPEN_FOREIGN


PayloadModel = TypeVar("PayloadModel", bound=BaseModel)
