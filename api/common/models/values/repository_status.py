# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the repository status module."""

# The git status drawn beside a session row.
from pydantic import BaseModel


class RepositoryStatusResponse(BaseModel):
    """Represent repository status response."""

    branch: str
    worktree: str | None
    dirty: bool
