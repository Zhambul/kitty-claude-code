# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

from dataclasses import dataclass

import github_project_values_data as project_values
from github_project_errors import GitHubProjectError as GitHubProjectError
from github_project_values import only_selection


@dataclass(frozen=True, slots=True)
class FieldOption:
    """Represent field option."""

    id: str
    name: str


@dataclass(frozen=True, slots=True)
class ProjectField:
    """Represent project field."""

    id: str
    name: str
    options: tuple[FieldOption, ...]


@dataclass(frozen=True, slots=True)
class ProjectSchema:
    """Represent project schema."""

    id: str
    title: str
    url: str
    fields: tuple[ProjectField, ...]

    def field(self, name: str) -> ProjectField:
        """Find a project field by its name, without case differences.

        Returns:
            The single matching field.

        """
        normalized_name = name.casefold()
        matches = [field for field in self.fields if field.name.casefold() == normalized_name]
        return only_selection(matches, f"project field named {name!r}")


@dataclass(frozen=True, slots=True)
class Issue:
    """Represent issue."""

    item_id: str
    content_id: str
    number: int
    title: str
    body: str
    url: str
    state: str
    status: str | None
    area: str | None
    work_type: str | None
    priority: str | None


@dataclass(frozen=True, slots=True)
class ProjectView:
    """Represent project view."""

    id: str
    number: int
    name: str
    layout: str
    filter: str | None


@dataclass(frozen=True, slots=True)
class NewIssue:
    """Define a new issue and its project fields."""

    title: str
    area: str
    work_type: str
    priority: str
    status: str = project_values.BACKLOG_STATUS
    body: str = ""


type IssuePage = tuple[list[Issue], str | None]
