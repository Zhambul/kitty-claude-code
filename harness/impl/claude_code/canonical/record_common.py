# Copyright (c) 2026 Zhambyl Yermagambet
"""Record common."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

FOREIGN = ConfigDict(extra="forbid", frozen=True, validate_by_name=True)
OPEN_FOREIGN = ConfigDict(extra="ignore", frozen=True, validate_by_name=True)


class ForeignMetadata(BaseModel):
    """Named vendor metadata that this adapter deliberately does not interpret."""

    model_config = OPEN_FOREIGN


class PermissionRule(BaseModel):
    """One native rule in a permission update entry."""

    model_config = FOREIGN
    tool_name: Annotated[str, Field(alias="toolName")]
    rule_content: Annotated[str | None, Field(alias="ruleContent")] = None


class PermissionUpdate(BaseModel):
    """One permission change that Claude offers or a hook returns."""

    model_config = FOREIGN
    type: str
    rules: list[PermissionRule] | None = None
    behavior: str | None = None
    destination: str | None = None
    mode: str | None = None


class ImageSource(BaseModel):
    """Represent image source."""

    model_config = OPEN_FOREIGN
    type: str | None = None
    media_type: str | None = None
    encoded_content: str | None = Field(default=None, alias="data")


class TranscriptRecordHeader(BaseModel):
    """Only the discriminator, used before the recognized record's strict model."""

    model_config = OPEN_FOREIGN
    type: str | None = None
