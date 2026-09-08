# Copyright (c) 2026 Zhambyl Yermagambet
"""Read and validate the Vite frontend manifest."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import PurePosixPath

from pydantic import BaseModel, ConfigDict, RootModel, ValidationError

from dashboard.frontend_build_inputs import ENTRY_MODULE, MANIFEST_PATH, FrontendBuildError


class ManifestEntry(BaseModel):
    """The Vite manifest fields used by the server."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    file: str | None = None
    css: tuple[str, ...] = ()
    imports: tuple[str, ...] = ()


class ViteManifest(RootModel[Mapping[str, ManifestEntry]]):
    """Represent Vite manifest."""


def asset_name(asset_reference: str | None, context: str) -> str:
    """Validate one manifest asset name.

    Returns:
        The safe asset name.

    Raises:
        FrontendBuildError: If the asset name is unsafe.

    """
    if asset_reference is None:
        message = f"{context} must be a string"
        raise FrontendBuildError(message)
    path = PurePosixPath(asset_reference)
    if path.is_absolute() or ".." in path.parts:
        message = f"{context} is not a safe build asset"
        raise FrontendBuildError(message)
    if not path.parts or path.parts[0] != "assets":
        message = f"{context} is not a safe build asset"
        raise FrontendBuildError(message)
    return asset_reference


def read_manifest() -> Mapping[str, ManifestEntry]:
    """Read the checked Vite manifest.

    Returns:
        The manifest mapping.

    Raises:
        FrontendBuildError: If the manifest is not readable or valid.

    """
    try:
        manifest = ViteManifest.model_validate_json(MANIFEST_PATH.read_bytes()).root
    except (OSError, UnicodeError, ValidationError) as error:
        message = "frontend manifest is unreadable"
        raise FrontendBuildError(message) from error
    if ENTRY_MODULE not in manifest:
        message = f"frontend manifest has no {ENTRY_MODULE} entry"
        raise FrontendBuildError(message)
    return manifest


def entry_assets(
    manifest: Mapping[str, ManifestEntry],
    key: str,
    visited: set[str],
) -> tuple[list[str], list[str]]:
    """Return recursive styles and modules for one manifest entry.

    Returns:
        The styles and modules.

    """
    if key in visited:
        return [], []
    visited.add(key)
    entry = manifest_entry(manifest, key)
    styles = entry_styles(entry, key)
    modules: list[str] = []
    for imported in entry.imports:
        imported_assets = entry_assets(manifest, imported, visited)
        styles.extend(imported_assets[0])
        modules.extend(imported_assets[1])
        modules.append(asset_name(manifest[imported].file, f"{imported}.file"))
    return styles, modules


def manifest_entry(manifest: Mapping[str, ManifestEntry], key: str) -> ManifestEntry:
    """Return one required manifest entry.

    Returns:
        The manifest entry.

    Raises:
        FrontendBuildError: If the entry is missing.

    """
    try:
        return manifest[key]
    except KeyError as error:
        message = f"frontend manifest import is missing: {key}"
        raise FrontendBuildError(message) from error


def entry_styles(manifest_entry: ManifestEntry, key: str) -> list[str]:
    """Return the styles of one manifest entry.

    Returns:
        The style asset names.

    """
    styles = []
    for index, name in enumerate(manifest_entry.css):
        styles.append(asset_name(name, f"{key}.css[{index}]"))
    return styles
