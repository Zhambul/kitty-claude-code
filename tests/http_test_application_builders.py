# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide http test application builders."""

from __future__ import annotations

from tests import (
    http_application_dependencies as application_dependencies,
    http_library_dependencies as library_dependencies,
    http_value_dependencies as standard_dependencies,
)

INDEX_DOCUMENT_NAME = "index.html"
MINIMUM_READ_ROUTES = 6


def api_routes(
    web: library_dependencies.fastapi.FastAPI,
) -> standard_dependencies.collections_abc.Iterator[library_dependencies.fastapi.routing.APIRoute]:
    """Every APIRoute in the application, flattened.

    `web.routes` is not a flat list in this FastAPI: `include_router` leaves an
    `_IncludedRouter` node that holds the original router rather than splicing its
    routes in. Both shapes are walked, and the test below asserts the walk really
    found the read plane — so a FastAPI that changes this again fails loudly here
    instead of quietly covering nothing.

    Yields:
        Each API route, including routes from nested routers.

    """
    pending = list(web.routes)
    while pending:
        route = pending.pop()
        if isinstance(route, library_dependencies.fastapi.routing.APIRoute):
            yield route
            continue
        nested = getattr(route, "original_router", None)
        nested = getattr(nested, "routes", None) or getattr(route, "routes", None)
        if nested:
            pending.extend(nested)


def assert_read_plane_was_checked(checked: list[str]) -> None:
    """Check that route validation covered the required read endpoints."""
    assert "/sessionData" in checked
    assert "/sessionData/{session_id}" in checked
    assert "/sessionData/{session_id}/entries" in checked
    assert "/api/harnesses/{harness}/catalog" in checked
    assert len(checked) >= MINIMUM_READ_ROUTES, checked


def assert_security_policy(headers: library_dependencies.http.client.HTTPMessage, route_path: str) -> None:
    """Check the required security headers and content security directives."""
    assert (headers["X-Content-Type-Options"], headers["X-Frame-Options"], headers["Referrer-Policy"]) == (
        "nosniff",
        "DENY",
        "strict-origin-when-cross-origin",
    ), route_path
    policy = headers["Content-Security-Policy"]
    assert "script-src 'self' blob:" in policy, route_path
    assert "frame-ancestors 'none'" in policy, route_path
    assert "connect-src 'self' wss://api.deepgram.com" in policy, route_path


def write_installed_app_assets(tmp_path: library_dependencies.Path) -> None:
    """Write the test index, manifest, and icons in the temporary directory."""
    manifest = b'{"icons":[{"src":"/static/icon-192.png"}]}'
    index = (
        b'<link rel="manifest" href="/static/manifest.webmanifest"><link '
        b'rel="apple-touch-icon" href="/static/apple-touch-icon.png"><!-- '
        b'vite-assets -->'
    )
    (tmp_path / INDEX_DOCUMENT_NAME).write_bytes(index)
    (tmp_path / "manifest.webmanifest").write_bytes(manifest)
    (tmp_path / "icon-192.png").write_bytes(b"icon-one")
    (tmp_path / "apple-touch-icon.png").write_bytes(b"apple-icon")


def assert_restart_keeps_asset_versions(
    first_policy: application_dependencies.api_config.Settings,
    second_policy: application_dependencies.api_config.Settings,
) -> bytes:
    """Check that a restart preserves the generated asset versions.

    Returns:
        The first index document for comparison with later asset changes.

    """
    first_document = application_dependencies.static_delivery.serve(first_policy, INDEX_DOCUMENT_NAME, "").body
    after_restart = application_dependencies.static_delivery.serve(second_policy, INDEX_DOCUMENT_NAME, "").body
    assert after_restart == first_document
    return bytes(first_document)


def assert_icon_change_updates_versions(
    tmp_path: library_dependencies.Path,
    policy: application_dependencies.api_config.Settings,
    first_document: bytes,
) -> None:
    """Change a test icon and check the index and manifest version updates."""
    (tmp_path / "icon-192.png").write_bytes(b"icon-two")
    changed_document = application_dependencies.static_delivery.serve(policy, INDEX_DOCUMENT_NAME, "").body
    assert changed_document != first_document
    manifest_reference = standard_dependencies.re.search(
        rb"/static/manifest\.webmanifest\?v=([a-f0-9]{64})",
        changed_document,
    )
    assert manifest_reference is not None
    response = application_dependencies.static_delivery.serve(
        policy,
        "manifest.webmanifest",
        manifest_reference.group(1).decode("ascii"),
    )
    assert response.headers["Cache-Control"] == "immutable"
    assert standard_dependencies.re.search(rb"/static/icon-192\.png\?v=[a-f0-9]{64}", response.body)


def expected_content_type(suffix: str) -> str:
    """Read the expected media type for a test asset suffix.

    Returns:
        The media type for the supplied supported suffix.

    """
    return {
        ".js": "text/javascript",
        ".css": "text/css",
        ".png": "image/png",
        ".webmanifest": "application/manifest+json",
    }[suffix]
