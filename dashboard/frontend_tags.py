# Copyright (c) 2026 Zhambyl Yermagambet
"""Render frontend manifest assets as HTML tags."""

from __future__ import annotations

import html
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from dashboard.frontend_build_inputs import BUILD_DIRECTORY, ENTRY_MODULE, FrontendBuildError
from dashboard.frontend_manifest import asset_name, entry_assets, read_manifest

if TYPE_CHECKING:
    from collections.abc import Sequence


def manifest_tags() -> bytes:
    """Render the frontend shell tags.

    Returns:
        The HTML tag bytes.

    """
    manifest = read_manifest()
    entry = manifest[ENTRY_MODULE]
    styles, modules = entry_assets(manifest, ENTRY_MODULE, set())
    entry_file = asset_name(entry.file, f"{ENTRY_MODULE}.file")
    return "\n".join((*tag_lines(styles, modules, entry_file), "")).encode()


def tag_lines(styles: list[str], modules: list[str], entry_file: str) -> list[str]:
    """Return the shell tag lines.

    Returns:
        The tag lines.

    """
    return [
        *(f'<link rel="stylesheet" href="/static/build/{html.escape(name, quote=True)}">' for name in unique(styles)),
        *(
            f'<link rel="modulepreload" crossorigin href="/static/build/{html.escape(name, quote=True)}">'
            for name in unique(modules)
        ),
        f'<script type="module" crossorigin src="/static/build/{html.escape(entry_file, quote=True)}"></script>',
    ]


def unique(asset_names: Sequence[str]) -> tuple[str, ...]:
    """Return asset names without changing their order.

    Returns:
        The unique asset names.

    """
    seen: set[str] = set()
    unique_names: list[str] = []
    for name in asset_names:
        if name not in seen:
            seen.add(name)
            unique_names.append(name)
    return tuple(unique_names)


def build_asset_path(asset_reference: str, build_directory: Path = BUILD_DIRECTORY) -> Path:
    """Resolve one safe build asset path.

    Returns:
        The asset path.

    Raises:
        FrontendBuildError: If the asset path escapes the build directory.

    """
    safe_name = asset_name(asset_reference, "build asset")
    build_root = build_directory.resolve()
    path = build_root.joinpath(*PurePosixPath(safe_name).parts).resolve()
    try:
        path.relative_to(build_root)
    except ValueError as error:
        message = "build asset escapes its directory"
        raise FrontendBuildError(message) from error
    return path
