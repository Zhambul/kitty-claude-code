# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import github_project_values_data as project_values
from github_project_errors import GitHubProjectError
from github_project_models import (
    FieldOption,
    Issue,
    ProjectField,
    ProjectSchema,
)
from github_project_output import (
    integer_field,
)
from github_project_values import (
    json_object,
    json_objects,
    text_field,
)


def _validate_field(
    schema: ProjectSchema,
    field_name: str,
    expected_options: tuple[str, ...],
) -> None:
    field = schema.field(field_name)
    actual_options = tuple(option.name for option in field.options)
    if actual_options != expected_options:
        message = f"{field_name} options do not match the SDK schema: {actual_options}"
        raise GitHubProjectError(message)


def validate_schema(schema: ProjectSchema) -> None:
    """Check that project fields have the required options."""
    expected = {
        project_values.STATUS_FIELD: project_values.STATUSES,
        project_values.AREA_FIELD: project_values.AREAS,
        project_values.TYPE_FIELD: project_values.WORK_TYPES,
        project_values.PRIORITY_FIELD: project_values.PRIORITIES,
    }
    for name, expected_options in expected.items():
        _validate_field(schema, name, expected_options)


def parse_project_field(field_document: dict[str, project_values.JsonValue]) -> ProjectField:
    """Read one project field and its options.

    Returns:
        The field described by the GitHub document.

    """
    raw_options = field_document.get("options", [])
    return ProjectField(
        id=text_field(field_document, project_values.IDENTIFIER_FIELD),
        name=text_field(field_document, project_values.NAME_FIELD),
        options=tuple(
            FieldOption(
                id=text_field(option, project_values.IDENTIFIER_FIELD),
                name=text_field(option, project_values.NAME_FIELD),
            )
            for option in json_objects(raw_options, "field options")
        ),
    )


def _named_field_value(field_value: dict[str, project_values.JsonValue]) -> tuple[str, str] | None:
    field = field_value.get("field")
    name = field_value.get(project_values.NAME_FIELD)
    field_name = field.get(project_values.NAME_FIELD) if isinstance(field, dict) else None
    if isinstance(field_name, str) and isinstance(name, str):
        return field_name, name
    return None


def _issue_field_values(project_item: dict[str, project_values.JsonValue]) -> dict[str, str]:
    field_values: dict[str, str] = {}
    connection = json_object(project_item.get("fieldValues"), "field value connection")
    for field_value in json_objects(connection.get(project_values.NODES_FIELD), "field values"):
        named_value = _named_field_value(field_value)
        if named_value is not None:
            field_values[named_value[0]] = named_value[1]
    return field_values


def parse_issue(project_item: dict[str, project_values.JsonValue], repository: str) -> Issue | None:
    """Read an issue from the selected repository.

    Returns:
        The issue, or None if the item has no content from the repository.

    """
    content = project_item.get("content")
    if not isinstance(content, dict):
        return None
    repository_document = content.get("repository")
    if not isinstance(repository_document, dict) or repository_document.get("nameWithOwner") != repository:
        return None
    field_values = _issue_field_values(project_item)
    return Issue(
        item_id=text_field(project_item, project_values.IDENTIFIER_FIELD),
        content_id=text_field(content, project_values.IDENTIFIER_FIELD),
        number=integer_field(content, project_values.NUMBER_FIELD),
        title=text_field(content, project_values.TITLE_FIELD),
        body=text_field(content, project_values.BODY_FIELD),
        url=text_field(content, "url"),
        state=text_field(content, project_values.STATE_FIELD),
        status=field_values.get(project_values.STATUS_FIELD),
        area=field_values.get(project_values.AREA_FIELD),
        work_type=field_values.get(project_values.TYPE_FIELD),
        priority=field_values.get(project_values.PRIORITY_FIELD),
    )
