# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import github_project_values_data as project_values
from github_project_documents import (
    parse_project_field,
    validate_schema,
)
from github_project_models import (
    Issue,
    NewIssue,
    ProjectSchema,
    ProjectView,
)
from github_project_values import (
    json_object,
    json_objects,
    priority_rank,
    require_choice,
    text_field,
)


def project_schema(
    response_document: dict[str, project_values.JsonValue],
    owner: str,
    project_number: int,
) -> ProjectSchema:
    """Read and check the project schema in a GitHub response.

    Returns:
        The project schema with its validated field options.

    """
    user = json_object(response_document.get("user"), f"GitHub user {owner!r}")
    project = json_object(user.get("projectV2"), f"project {project_number}")
    fields_payload = json_object(project.get("fields"), "field connection").get(project_values.NODES_FIELD)
    fields = tuple(
        parse_project_field(field_document)
        for field_document in json_objects(fields_payload, "project fields")
        if field_document.get(project_values.IDENTIFIER_FIELD)
    )
    schema = ProjectSchema(
        id=text_field(project, project_values.IDENTIFIER_FIELD),
        title=text_field(project, project_values.TITLE_FIELD),
        url=text_field(project, "url"),
        fields=fields,
    )
    validate_schema(schema)
    return schema


def is_exact_issue_match(issue: Issue, text: str) -> bool:
    """Return true when text selects an issue exactly.

    Returns:
        True when text selects an issue exactly.

    """
    if text in {str(issue.number), issue.url}:
        return True
    return issue.title.casefold() == text.casefold()


def is_partial_issue_match(issue: Issue, text: str) -> bool:
    """Return true when text occurs in an issue title.

    Returns:
        True when text occurs in an issue title.

    """
    return text.casefold() in issue.title.casefold()


def backlog_order(issue: Issue) -> tuple[int, int]:
    """Return the stable backlog sort order for one issue.

    Returns:
        The stable backlog sort order for one issue.

    """
    return priority_rank(issue.priority), issue.number


def is_exact_view_match(view: ProjectView, query: str) -> bool:
    """Return true when query selects a project view exactly.

    Returns:
        True when query selects a project view exactly.

    """
    if query in {view.id, str(view.number)}:
        return True
    return view.name.casefold() == query.casefold()


def is_open_issue_duplicate(issue: Issue, new_issue: NewIssue) -> bool:
    """Return true when an open issue has the new issue title.

    Returns:
        True when an open issue has the new issue title.

    """
    if issue.state != "OPEN":
        return False
    return issue.title.casefold() == new_issue.title.casefold()


def validate_issue_filters(
    status: str | None,
    area: str | None,
    work_type: str | None,
    priority: str | None,
) -> None:
    """Check each supplied issue filter against the supported choices."""
    if status is not None:
        require_choice(status, project_values.STATUSES, project_values.STATUS_CHOICE)
    if area is not None:
        require_choice(area, project_values.AREAS, project_values.AREA_CHOICE)
    if work_type is not None:
        require_choice(work_type, project_values.WORK_TYPES, "work type")
    if priority is not None:
        require_choice(priority, project_values.PRIORITIES, project_values.PRIORITY_CHOICE)
