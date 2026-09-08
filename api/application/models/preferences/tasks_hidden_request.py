# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the tasks hidden request module."""

# One session's task-list visibility switch.
from pydantic import BaseModel


class TasksHiddenRequest(BaseModel):
    """Represent tasks hidden request."""

    hidden: bool
