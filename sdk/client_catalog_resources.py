# Copyright (c) 2026 Zhambyl Yermagambet
"""Split SDK client implementation."""

from __future__ import annotations

import base64
from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

from sdk import application_models, transport
from sdk.client_adapters import (
    HARNESS_CATALOG,
    HARNESS_LIST,
    INSIGHTS,
    RESUMABLE_SESSIONS,
    UPLOAD,
)

if TYPE_CHECKING:
    from sdk.client_models import SessionRef


class HarnessesResource:
    """Represent harnesses resource."""

    def __init__(self, transport: transport.HttpTransport) -> None:
        """Initialize the harnesses resource."""
        self.transport = transport

    def list(self) -> tuple[application_models.harness_description_response.HarnessDescriptionResponse, ...]:
        """Return list.

        Returns:
            List.

        """
        return self.transport.get("/api/harnesses", HARNESS_LIST)

    def catalog(
        self,
        harness: str,
        *,
        session: SessionRef | None = None,
        workspace: str | None = None,
    ) -> application_models.harness_catalog_response.HarnessCatalogResponse:
        """Return the catalog.

        Returns:
            Catalog.

        """
        session_id = None if session is None else session.session_id
        query = urlencode(
            {
                parameter_name: parameter_content
                for parameter_name, parameter_content in {
                    "session_id": session_id,
                    "working_directory": workspace,
                }.items()
                if parameter_content is not None
            },
        )
        suffix = f"?{query}" if query else ""
        return self.transport.get(
            f"/api/harnesses/{quote(harness, safe='')}/catalog{suffix}",
            HARNESS_CATALOG,
        )


class InsightsResource:
    """Represent insights resource."""

    def __init__(self, transport: transport.HttpTransport) -> None:
        """Initialize the insights resource."""
        self.transport = transport

    def state(self) -> application_models.application_insights_response.ApplicationInsightsResponse:
        """Return the state.

        Returns:
            State.

        """
        return self.transport.get("/api/insights", INSIGHTS)

    def resumable_sessions(
        self,
        *,
        workspace: str,
        search: str | None = None,
    ) -> tuple[application_models.resumable_session_response.ResumableSessionResponse, ...]:
        """Return the resumable sessions.

        Returns:
            Resumable sessions.

        """
        query = urlencode(
            {
                parameter_name: parameter_content
                for parameter_name, parameter_content in {"working_directory": workspace, "search": search}.items()
                if parameter_content is not None
            },
        )
        return self.transport.get(f"/api/resumable-sessions?{query}", RESUMABLE_SESSIONS)


class UploadsResource:
    """Represent uploads resource."""

    def __init__(self, transport: transport.HttpTransport) -> None:
        """Initialize the uploads resource."""
        self.transport = transport

    def stage(
        self,
        *,
        name: str,
        media_type: str,
        file_content: bytes,
        session: SessionRef | None = None,
    ) -> application_models.upload_response.UploadResponse:
        """Return the stage.

        Returns:
            Stage.

        """
        _status, response = self.transport.post(
            "/api/application/uploads",
            application_models.upload_request.UploadRequest(
                name=name,
                mime=media_type,
                data=base64.b64encode(file_content).decode("ascii"),
                session_id=None if session is None else session.session_id,
            ),
            UPLOAD,
            {200},
        )
        return response
