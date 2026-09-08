# Copyright (c) 2026 Zhambyl Yermagambet
"""Deliver static application files."""

from http import HTTPStatus
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import Response

from api.application import static_documents
from api.dependencies import Policy
from dashboard.config import STATIC
from dashboard.frontend_build import FrontendBuildError, build_asset_path


def static_content(name: str) -> bytes:
    """Build the response content for one static file.

    Returns:
        The response content.

    """
    content = static_documents.read_static(name)
    if name == "index.html":
        return static_documents.index_document(content)
    if name == "manifest.webmanifest":
        return static_documents.manifest_document(content)
    return content


def serve(policy: Policy, name: str, version: str) -> Response:
    """Serve one named static file.

    Returns:
        The static response.

    Raises:
        HTTPException: If the file is not allowed or cannot be read.

    """
    content_type = STATIC.get(name)
    if not content_type:
        raise HTTPException(HTTPStatus.NOT_FOUND, "not found")
    try:
        content = static_content(name)
    except (FrontendBuildError, OSError) as error:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, "unreadable") from error
    expected_version = static_documents.content_version(content).decode("ascii")
    cache = policy.cache_static if version and version == expected_version else "no-store"
    headers = {"Cache-Control": cache}
    return Response(content=content, media_type=content_type, headers=headers)


def build_content_type(asset_name: str) -> str | None:
    """Return the content type for one built asset.

    Returns:
        The content type, or None for an unsupported asset.

    """
    suffix = Path(asset_name).suffix
    if suffix == ".css":
        return "text/css; charset=utf-8"
    if suffix == ".js":
        return "text/javascript; charset=utf-8"
    return None


def read_build_content(asset_name: str) -> bytes:
    """Read one built asset.

    Returns:
        The asset content.

    """
    return build_asset_path(asset_name).read_bytes()


def serve_build(policy: Policy, asset_name: str) -> Response:
    """Serve one built asset.

    Returns:
        The asset response.

    Raises:
        HTTPException: If the asset is unsupported or cannot be read.

    """
    content_type = build_content_type(asset_name)
    if content_type is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "not found")
    try:
        content = read_build_content(asset_name)
    except FrontendBuildError as error:
        raise HTTPException(HTTPStatus.NOT_FOUND, "not found") from error
    except OSError as error:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, "unreadable") from error
    headers = {"Cache-Control": policy.cache_static}
    return Response(content=content, media_type=content_type, headers=headers)
