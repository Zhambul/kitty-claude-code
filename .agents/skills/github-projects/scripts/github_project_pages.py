# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import github_project_values_data as project_values
from github_project_documents import (
    parse_issue,
)
from github_project_errors import GitHubProjectError
from github_project_models import (
    Issue,
    NewIssue,
    ProjectView,
)
from github_project_output import (
    integer_field,
    optional_text_field,
)
from github_project_values import (
    json_object,
    json_objects,
    require_choice,
    text_field,
)
from github_project_view_mutation import parse_project_view


def filter_issues(
    issues: list[Issue],
    status: str | None,
    area: str | None,
    work_type: str | None,
    priority: str | None,
) -> list[Issue]:
    """Select issues that match all supplied filters.

    Returns:
        The matching issues in their original order.

    """
    return [
        issue
        for issue in issues
        if (status is None or issue.status == status)
        and (area is None or issue.area == area)
        and (work_type is None or issue.work_type == work_type)
        and (priority is None or issue.priority == priority)
    ]


def project_item_connection(
    response_document: dict[str, project_values.JsonValue],
) -> dict[str, project_values.JsonValue]:
    """Read the item connection from a project response.

    Returns:
        The item connection document.

    """
    user = json_object(response_document.get("user"), "GitHub user")
    project = json_object(user.get("projectV2"), project_values.PROJECT_VARIABLE)
    return json_object(project.get("items"), "project item connection")


def issues_from_connection(connection: dict[str, project_values.JsonValue], repository: str) -> list[Issue]:
    """Read repository issues from one project page.

    Returns:
        The issues from the selected repository, in page order.

    """
    issues: list[Issue] = []
    for project_item in json_objects(connection.get(project_values.NODES_FIELD), "project items"):
        issue = parse_issue(project_item, repository)
        if issue is not None:
            issues.append(issue)
    return issues


def next_page_cursor(connection: dict[str, project_values.JsonValue]) -> str | None:
    """Read the cursor for the next project page.

    Returns:
        The cursor, or None if this is the last page.

    Raises:
        GitHubProjectError: If another page exists but its cursor is absent.

    """
    page_information = json_object(connection.get("pageInfo"), "page information")
    if not page_information.get("hasNextPage"):
        return None
    cursor = optional_text_field(page_information, "endCursor")
    if cursor is None:
        msg = "GitHub did not return a cursor for the next project item page"
        raise GitHubProjectError(msg)
    return cursor


def updated_view(response_document: dict[str, project_values.JsonValue]) -> ProjectView:
    """Read the project view returned by an update.

    Returns:
        The updated view.

    """
    result = json_object(response_document.get("updateProjectV2View"), "update view result")
    return parse_project_view(json_object(result.get("projectV2View"), "project view"))


def validate_new_issue(new_issue: NewIssue) -> None:
    """Check the title and field choices before issue creation.

    Raises:
        GitHubProjectError: If the title is empty.

    """
    if not new_issue.title.strip():
        msg = "Issue title must not be empty"
        raise GitHubProjectError(msg)
    require_choice(new_issue.area, project_values.AREAS, project_values.AREA_CHOICE)
    require_choice(new_issue.work_type, project_values.WORK_TYPES, "work type")
    require_choice(new_issue.priority, project_values.PRIORITIES, project_values.PRIORITY_CHOICE)
    require_choice(new_issue.status, project_values.STATUSES, project_values.STATUS_CHOICE)


def new_issue_from_document(
    created: dict[str, project_values.JsonValue],
    item_id: str,
    new_issue: NewIssue,
) -> Issue:
    """Combine the created issue with its requested project fields.

    Returns:
        The created issue with its project item identifier.

    """
    return Issue(
        item_id=item_id,
        content_id=text_field(created, "node_id"),
        number=integer_field(created, project_values.NUMBER_FIELD),
        title=text_field(created, project_values.TITLE_FIELD),
        body=text_field(created, project_values.BODY_FIELD),
        url=text_field(created, "html_url"),
        state=text_field(created, project_values.STATE_FIELD).upper(),
        status=new_issue.status,
        area=new_issue.area,
        work_type=new_issue.work_type,
        priority=new_issue.priority,
    )
