# Copyright (c) 2026 Zhambyl Yermagambet
"""Build static application documents."""

import hashlib
import re
from pathlib import Path

from dashboard.config import STATIC_DIR
from dashboard.frontend_build import FrontendBuildError, manifest_tags

VITE_MARKER = b"<!-- vite-assets -->"
INDEX_ICON_REFERENCE = re.compile(
    rb"(/static/(?P<name>(?:apple-touch-icon|icon-[a-z0-9-]+)\.png))",
)
MANIFEST_ICON_REFERENCE = re.compile(
    rb"(/static/(?P<name>icon-[a-z0-9-]+\.png))",
)


def read_static(name: str) -> bytes:
    """Read one static file.

    Returns:
        The file content.

    """
    return (Path(STATIC_DIR) / name).read_bytes()


def content_version(content: bytes) -> bytes:
    """Return the digest for static content.

    Returns:
        The ASCII digest.

    """
    return hashlib.sha256(content).hexdigest().encode("ascii")


def versioned_static_reference(reference_match: re.Match[bytes]) -> bytes:
    """Add the content version to one static reference.

    Returns:
        The versioned reference.

    """
    name = reference_match.group("name").decode("ascii")
    return b"".join(
        (
            reference_match.group(1),
            b"?v=",
            content_version(read_static(name)),
        ),
    )


def manifest_document(manifest_content: bytes) -> bytes:
    """Add content versions to manifest icon references.

    Returns:
        The changed manifest.

    """
    return MANIFEST_ICON_REFERENCE.sub(versioned_static_reference, manifest_content)


def stamped_index(index_content: bytes) -> bytes:
    """Add content versions to index icon references.

    Returns:
        The changed index.

    """
    versioned_index = INDEX_ICON_REFERENCE.sub(versioned_static_reference, index_content)
    manifest_content = manifest_document(read_static("manifest.webmanifest"))
    versioned_manifest = b"".join(
        (
            b"/static/manifest.webmanifest?v=",
            content_version(manifest_content),
        ),
    )
    return versioned_index.replace(b"/static/manifest.webmanifest", versioned_manifest)


def index_document(index_content: bytes) -> bytes:
    """Add built assets and content versions to the index.

    Returns:
        The changed index.

    Raises:
        FrontendBuildError: If the index has no single asset marker.

    """
    if index_content.count(VITE_MARKER) != 1:
        message = "index.html must contain one Vite asset marker"
        raise FrontendBuildError(message)
    return stamped_index(index_content.replace(VITE_MARKER, manifest_tags()))
