# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared value types for stored session feed entries."""

from dataclasses import dataclass
from enum import StrEnum

from domain.stored import STORED


class RunState(StrEnum):
    """Show how an operation that runs ended."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TurnState(StrEnum):
    """Show how an agent turn ended."""

    FINISHED = "finished"
    ABORTED = "aborted"


class FileState(StrEnum):
    """Show if a file or resource operation succeeded."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True)
class EntryBody:
    """Provide the stored-shape rules for each entry body."""

    __pydantic_config__ = STORED
