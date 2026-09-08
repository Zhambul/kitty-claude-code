# Copyright (c) 2026 Zhambyl Yermagambet
"""Define typed kitty remote-control messages."""

from pydantic import BaseModel, ConfigDict, Field


class KittyRcResponse(BaseModel):
    """Represent a kitty remote-control reply."""

    model_config = ConfigDict(extra="ignore", frozen=True)
    ok: bool = False
    response_text: str | None = Field(default=None, alias="data")


class SetTabColorRcPayload(BaseModel):
    """Represent a set-tab-color payload."""

    model_config = ConfigDict(frozen=True)
    match: str
    colors: dict[str, int | None]


class GetTextRcPayload(BaseModel):
    """Represent a get-text payload."""

    model_config = ConfigDict(frozen=True)
    match: str
    extent: str
    ansi: bool = False


class LsRcPayload(BaseModel):
    """Represent an ls payload."""

    model_config = ConfigDict(frozen=True)


KittyRcPayload = SetTabColorRcPayload | GetTextRcPayload | LsRcPayload


class KittyRcCommand(BaseModel):
    """Represent a kitty remote-control command."""

    model_config = ConfigDict(frozen=True)
    cmd: str
    version: tuple[int, int, int]
    no_response: bool
    payload: KittyRcPayload
