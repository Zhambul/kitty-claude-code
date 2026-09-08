# Copyright (c) 2026 Zhambyl Yermagambet
"""Closed states for session goals, tasks, and selections."""

from enum import StrEnum


class ModelChangeReason(StrEnum):
    """Show why the active model changed."""

    SELECTED = "selected"
    AUTOMATIC_FALLBACK = "automatic_fallback"
    REPORTED_BY_HARNESS = "reported_by_harness"


class EffortChangeReason(StrEnum):
    """Show why the active effort changed."""

    SELECTED = "selected"
    REPORTED_BY_HARNESS = "reported_by_harness"


class OpenWorkKind(StrEnum):
    """Identify a kind of work that can stay open."""

    TURN = "turn"
    SHELL = "shell"
    ASSIGNMENT = "assignment"


class TitleOrigin(StrEnum):
    """Identify the source of a session title."""

    CUSTOM = "custom"
    AUTOMATIC = "automatic"
    SUMMARY = "summary"


class GoalState(StrEnum):
    """Show the current state of a user goal."""

    ACTIVE = "active"
    PAUSED = "paused"
    BLOCKED = "blocked"
    USAGE_LIMITED = "usage_limited"
    BUDGET_LIMITED = "budget_limited"
    COMPLETED = "completed"
    CLEARED = "cleared"


class ShellFollowUntil(StrEnum):
    """Show when the application stops reading a shell output file."""

    SHELL_FINISHED = "shell_finished"
    SESSION_FINISHED = "session_finished"


class TaskState(StrEnum):
    """Show the current state of a session task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELETED = "deleted"
