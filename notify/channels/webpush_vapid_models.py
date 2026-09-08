# Copyright (c) 2026 Zhambyl Yermagambet
"""Own Web Push vapid models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ASCII_ENCODING = "ascii"


class VapidHeader(BaseModel):
    """Represent vapid header."""

    typ: Literal["JWT"] = "JWT"
    alg: Literal["ES256"] = "ES256"


class VapidClaims(BaseModel):
    """Represent vapid claims."""

    audience: str = Field(serialization_alias="aud")
    exp: int
    sub: str


class PushErrorResponse(BaseModel):
    """Represent push error response."""

    model_config = ConfigDict(extra="ignore")

    reason: str | None = None
