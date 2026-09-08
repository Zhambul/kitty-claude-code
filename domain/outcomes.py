# Copyright (c) 2026 Zhambyl Yermagambet
"""Closed states for operations and their output."""

from enum import StrEnum


class Outcome(StrEnum):
    """Show the final outcome of a canonical operation."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


class ExecutionMode(StrEnum):
    """Show how a shell command runs."""

    FOREGROUND = "foreground"
    BACKGROUND = "background"
    MONITOR = "monitor"


class FileAction(StrEnum):
    """Show the operation that changed or read a file."""

    READ = "read"
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RENAMED = "renamed"


class PlanState(StrEnum):
    """Show how a person resolved a proposed plan."""

    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"


class WorktreeAction(StrEnum):
    """Show if an actor entered or left a worktree."""

    ENTERED = "entered"
    EXITED = "exited"


class ProgressStream(StrEnum):
    """Identify the source stream of an output chunk."""

    OUTPUT = "output"
    ERROR = "error"
    STATUS = "status"


class OutputMode(StrEnum):
    """Show how an output chunk changes earlier output."""

    APPEND = "append"
    REPLACE = "replace"
