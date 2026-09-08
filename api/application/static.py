# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide the static module."""

# api/application/static.py — the SPA shell and its content-addressed assets.
#
# This is policy, not plumbing, so it stays hand-written: no user-path
# resolution ever. FastAPI owns the document and reads Vite's manifest to add
# content-addressed CSS and module tags. The unbundled icons and web manifest
# use their own content digests because Vite does not own those files.
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import Response

from api.application import static_delivery
from api.dependencies import Policy
from api.responses import errors

VersionQuery = Annotated[str, Query(alias="v")]

router = APIRouter(
    responses=errors(
        {
            404: "Not on the static content-type whitelist.",
            500: "On the whitelist, but unreadable on disk.",
        },
    ),
)


@router.get("/")
def index(policy: Policy, version: VersionQuery = "") -> Response:
    """Return the index.

    Returns:
        Index.

    """
    return static_delivery.serve(policy, "index.html", version)


@router.get("/static/build/{asset_name:path}")
def build_asset(asset_name: str, policy: Policy) -> Response:
    """Build asset.

    Returns:
        The response.

    """
    return static_delivery.serve_build(policy, asset_name)


@router.get("/static/{name}")
def static(name: str, policy: Policy, version: VersionQuery = "") -> Response:
    """Return the static.

    Returns:
        Static.

    """
    return static_delivery.serve(policy, name, version)


@router.get("/sw.js")
def service_worker(policy: Policy, version: VersionQuery = "") -> Response:
    # the push service worker, served at the root so its scope is the whole
    # origin — not under /static/, which would scope it to /static/ and leave
    # every page outside that prefix unreachable by a push notification.
    """Return the service worker.

    Returns:
        Service worker.

    """
    return static_delivery.serve(policy, "sw.js", version)


@router.get("/favicon.ico")
def favicon(policy: Policy, version: VersionQuery = "") -> Response:
    # the raster fallback favicon, at the root path clients probe on their own
    # when the declared SVG icon is unusable. Undeclared on purpose — see
    # dashboard/config.py STATIC for the whitelist this is deliberately not in.
    """Return the favicon.

    Returns:
        Favicon.

    """
    return static_delivery.serve(policy, "favicon.ico", version)
