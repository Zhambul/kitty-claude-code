# Copyright (c) 2026 Zhambyl Yermagambet
"""Validate and describe the browser bundle that FastAPI serves."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from dashboard import frontend_build_inputs, frontend_manifest, frontend_tags

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

FrontendBuildError = frontend_build_inputs.FrontendBuildError
ManifestEntry = frontend_manifest.ManifestEntry
ViteManifest = frontend_manifest.ViteManifest
source_digest = frontend_build_inputs.source_digest
write_build_stamp = frontend_build_inputs.write_build_stamp
read_manifest = frontend_manifest.read_manifest
manifest_tags = frontend_tags.manifest_tags
BUILD_DIRECTORY = frontend_build_inputs.BUILD_DIRECTORY
MANIFEST_PATH = frontend_build_inputs.MANIFEST_PATH
STAMP_PATH = frontend_build_inputs.STAMP_PATH


def build_asset_path(asset_reference: str) -> Path:
    """Resolve one safe build asset path.

    Returns:
        The asset path.

    """
    return frontend_tags.build_asset_path(asset_reference, BUILD_DIRECTORY)


def validate_frontend_build() -> None:
    """Fail when the daemon would serve missing or stale bytes."""
    if not MANIFEST_PATH.is_file() or not STAMP_PATH.is_file():
        message = "frontend build is missing; run `make build-frontend`"
        raise FrontendBuildError(message)
    try:
        stamped = STAMP_PATH.read_text(encoding="ascii").strip()
    except OSError as error:
        message = "frontend build stamp is unreadable"
        raise FrontendBuildError(message) from error
    if stamped != source_digest():
        message = "frontend build is stale; run `make build-frontend`"
        raise FrontendBuildError(message)
    read_manifest()


def main(arguments: Sequence[str] | None = None) -> int:
    """Write the build stamp after Vite completes.

    Returns:
        The process result.

    """
    if tuple(arguments or ()) != ("--stamp",):
        message = "usage: python -m dashboard.frontend_build --stamp"
        raise FrontendBuildError(message)
    write_build_stamp()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
