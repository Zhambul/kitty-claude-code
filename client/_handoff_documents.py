# Copyright (c) 2026 Zhambyl Yermagambet
"""Define the documents for the terminal handoff channel."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict


class PaneDocument(BaseModel):
    """Store pane process and copy target data."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    pid: int
    targets: Mapping[str, str]


class ViewDocument(BaseModel):
    """Store expanded terminal entry identifiers."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    opened: tuple[str, ...]
