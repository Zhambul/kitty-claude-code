# Copyright (c) 2026 Zhambyl Yermagambet
"""Split GitHub Projects SDK implementation."""

from __future__ import annotations

import json
import os
import shutil
import subprocess  # noqa: S404 -- Read the token from the installed GitHub CLI when needed.
from http import HTTPStatus
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import github_project_values_data as project_values
from github_project_errors import GitHubProjectError
from github_project_values import json_value


class Transport(Protocol):
    """Represent transport."""

    def request(
        self,
        method: str,
        path: str,
        request_document: dict[str, project_values.JsonValue] | None = None,
    ) -> project_values.JsonValue:
        """Process request."""
        ...


class HttpTransport:
    """Send authenticated requests to GitHub without automatic retries."""

    def __init__(self, token: str, base_url: str = project_values.API_BASE) -> None:
        """Store the authentication token and API address.

        Raises:
            GitHubProjectError: If the token is empty or the API address does not use HTTPS.

        """
        if not token:
            msg = "GitHub authentication token is missing"
            raise GitHubProjectError(msg)
        if not base_url.startswith("https://"):
            msg = "GitHub API address must use https"
            raise GitHubProjectError(msg)
        self._token = token
        self._base_url = base_url.rstrip("/")

    @classmethod
    def from_environment(cls) -> HttpTransport:
        """Create the object from environment.

        Returns:
            The object from environment.

        """
        token = os.environ.get("GITHUB_TOKEN")
        if not token:
            token = os.environ.get("GH_TOKEN")
        if not token:
            token = _gh_token()
        return cls(token)

    def request(
        self,
        method: str,
        path: str,
        request_document: dict[str, project_values.JsonValue] | None = None,
    ) -> project_values.JsonValue:
        """Send one authenticated API request.

        Returns:
            The decoded response, or an empty object for a response with no content.

        """
        request = self._build_request(method, path, request_document)
        return _send_request(request)

    def _build_request(
        self,
        method: str,
        path: str,
        request_document: dict[str, project_values.JsonValue] | None,
    ) -> Request:
        body = None
        if request_document is not None:
            encoder = json.JSONEncoder()
            body = encoder.encode(request_document).encode()
        return Request(  # noqa: S310 -- The base URL accepts only HTTPS.
            f"{self._base_url}{path}",
            data=body,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
                "User-Agent": "baqylau-github-projects-sdk",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method=method,
        )


def _send_request(request: Request) -> project_values.JsonValue:
    try:
        with urlopen(request, timeout=project_values.REQUEST_TIMEOUT_SECONDS) as response:  # noqa: S310 -- Requests use the validated HTTPS base URL.
            if response.status == HTTPStatus.NO_CONTENT:
                return {}
            decoded: object = json.load(response)
            return json_value(decoded)
    except HTTPError as error:
        detail = error.read().decode(errors="replace").strip()
        message = f"GitHub returned HTTP {error.code}: {detail}"
        raise GitHubProjectError(message) from error
    except URLError as error:
        message = f"Could not reach GitHub: {error.reason}"
        raise GitHubProjectError(message) from error
    except json.JSONDecodeError as error:
        message = "GitHub returned invalid JSON"
        raise GitHubProjectError(message) from error


def _gh_token() -> str:
    executable = shutil.which("gh")
    if executable is None:
        msg = "Set GITHUB_TOKEN or authenticate with gh"
        raise GitHubProjectError(msg)
    try:
        result = subprocess.run(  # noqa: S603 -- Use the resolved GitHub CLI with fixed auth arguments, without a shell.
            [executable, "auth", "token"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
        msg = "Set GITHUB_TOKEN or authenticate with gh"
        raise GitHubProjectError(msg) from error
    return result.stdout.strip()
