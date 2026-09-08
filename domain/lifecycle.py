# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared lifecycle state for sessions and actors."""

from enum import StrEnum


class LifecycleState(StrEnum):
    """Show if a session or actor can still produce activity."""

    RUNNING = "running"
    FINISHED = "finished"
