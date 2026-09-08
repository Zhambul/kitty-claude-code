# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import github_project_values_data as project_values
from github_project_errors import GitHubProjectError


def priority_rank(priority: str | None) -> int:
    """Read the numeric rank from a priority label.

    Returns:
        The numeric rank, or the unranked priority value.

    """
    match = project_values.PRIORITY_PATTERN.match(priority or "")
    return int(match.group("rank")) if match else project_values.UNRANKED_PRIORITY


def require_choice(selection: str, choices: tuple[str, ...], description: str) -> None:
    """Check that a selection is available.

    Raises:
        GitHubProjectError: If the selection is not in the available choices.

    """
    if selection not in choices:
        choice_text = ", ".join(choices)
        invalid_choice = f"Invalid {description}: {selection}. Choose from: {choice_text}"
        raise GitHubProjectError(
            invalid_choice,
        )


def json_object(json_content: project_values.JsonValue, description: str) -> dict[str, project_values.JsonValue]:
    """Check that a JSON value is an object.

    Returns:
        The validated JSON object.

    Raises:
        GitHubProjectError: If the value is not an object.

    """
    if not isinstance(json_content, dict):
        invalid_object = f"GitHub returned an invalid {description}"
        raise GitHubProjectError(invalid_object)
    return json_content


def json_objects(json_content: project_values.JsonValue, description: str) -> list[dict[str, project_values.JsonValue]]:
    """Check that a JSON value is a list of objects.

    Returns:
        The validated JSON objects.

    Raises:
        GitHubProjectError: If the value is not a list of objects.

    """
    if not isinstance(json_content, list):
        msg = f"GitHub returned invalid {description}"
        raise GitHubProjectError(msg)
    documents: list[dict[str, project_values.JsonValue]] = []
    for document in json_content:
        if not isinstance(document, dict):
            msg = f"GitHub returned invalid {description}"
            raise GitHubProjectError(msg)
        documents.append(document)
    return documents


def json_value(candidate: object) -> project_values.JsonValue:
    """Validate a decoded JSON value and its child values.

    Returns:
        The validated JSON value.

    Raises:
        GitHubProjectError: If a value or object key cannot be represented in JSON.

    """
    if candidate is None:
        return candidate
    if isinstance(candidate, (bool, float, int, str)):
        return candidate
    if isinstance(candidate, list):
        return [json_value(element) for element in candidate]
    if not isinstance(candidate, dict):
        msg = "GitHub returned a value that JSON cannot represent"
        raise GitHubProjectError(msg)
    converted: dict[str, project_values.JsonValue] = {}
    for property_name, content in candidate.items():
        if not isinstance(property_name, str):
            msg = "GitHub returned a value that JSON cannot represent"
            raise GitHubProjectError(msg)
        converted[property_name] = json_value(content)
    return converted


def only_selection[Selection](selections: list[Selection], description: str) -> Selection:
    """Require exactly one matching selection.

    Returns:
        The only selection.

    Raises:
        GitHubProjectError: If there are zero or multiple selections.

    """
    if not selections:
        msg = f"Could not find {description}"
        raise GitHubProjectError(msg)
    if len(selections) > 1:
        msg = f"Found more than one {description}"
        raise GitHubProjectError(msg)
    return selections[0]


def text_field(document: dict[str, project_values.JsonValue], field: str) -> str:
    """Read a required text field.

    Returns:
        The field's text value.

    Raises:
        GitHubProjectError: If the field is absent or is not text.

    """
    field_content = document.get(field)
    if not isinstance(field_content, str):
        msg = f"GitHub field is not text: {field}"
        raise GitHubProjectError(msg)
    return field_content
