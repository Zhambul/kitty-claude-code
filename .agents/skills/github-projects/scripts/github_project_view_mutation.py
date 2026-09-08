# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

from dataclasses import dataclass

import github_project_values_data as project_values
from github_project_models import ProjectView
from github_project_output import integer_field, optional_text_field
from github_project_values import text_field


@dataclass(slots=True)
class ViewMutation:
    """Build the input for a project view update."""

    variables: dict[str, project_values.JsonValue]
    declarations: list[str]
    assignments: list[str]

    @classmethod
    def for_view(cls, view_id: str) -> ViewMutation:
        """Create an update for one project view.

        Returns:
            An update for one project view.

        """
        return cls(
            variables={"view": view_id},
            declarations=["$view: ID!"],
            assignments=["viewId: $view"],
        )

    def add(self, field_name: str, field_content: project_values.JsonValue, declaration: str, assignment: str) -> None:
        """Add one optional input to the update."""
        self.variables[field_name] = field_content
        self.declarations.append(declaration)
        self.assignments.append(assignment)

    def query(self) -> str:
        """Build the GraphQL update mutation.

        Returns:
            The GraphQL update mutation.

        """
        declarations = ", ".join(self.declarations)
        assignments = ", ".join(self.assignments)
        return (
            f"mutation({declarations}) {{ updateProjectV2View(input: {{{assignments}}}) "
            "{ projectV2View { id number name layout filter } } }"
        )


def parse_project_view(view_document: dict[str, project_values.JsonValue]) -> ProjectView:
    """Read a project view from a GitHub document.

    Returns:
        The view and its display settings.

    """
    return ProjectView(
        id=text_field(view_document, project_values.IDENTIFIER_FIELD),
        number=integer_field(view_document, project_values.NUMBER_FIELD),
        name=text_field(view_document, project_values.NAME_FIELD),
        layout=text_field(view_document, "layout"),
        filter=optional_text_field(view_document, "filter"),
    )
