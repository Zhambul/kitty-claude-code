# Copyright (c) 2026 Zhambyl Yermagambet
"""Support for rollout catalog tests."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from functools import partial
from typing import TYPE_CHECKING

from harness.impl.codex.canonical import source_catalog as codex_source_catalog

if TYPE_CHECKING:
    from pathlib import Path

    import pytest

type NativeScandir = Callable[
    [str | os.PathLike[str]],
    Iterator[os.DirEntry[str]],
]


type CatalogPaths = Callable[[], tuple[str, ...]]


def record_scanned_directory(
    scanned_directories: list[str],
    native_scandir: NativeScandir,
    directory: str | os.PathLike[str],
) -> Iterator[os.DirEntry[str]]:
    """Record a directory scan and call the native scanner.

    Returns:
        The native directory-entry iterator.

    """
    scanned_directories.append(os.fspath(directory))
    return native_scandir(directory)


def tracked_rollout_catalog(
    codex_home: Path,
    monkeypatch: pytest.MonkeyPatch,
    scanned_directories: list[str],
) -> codex_source_catalog.RolloutCatalog:
    """Build a rollout catalog with directory-scan recording enabled.

    Returns:
        The catalog for the supplied Codex directory.

    """
    monkeypatch.setattr(
        "harness.impl.codex.canonical.source_catalog.os.scandir",
        partial(record_scanned_directory, scanned_directories, os.scandir),
    )
    return codex_source_catalog.RolloutCatalog(str(codex_home))


def record_catalog_paths(
    catalog_invocations: list[None],
    native_paths: CatalogPaths,
) -> tuple[str, ...]:
    """Record a catalog query and call its native implementation.

    Returns:
        The paths returned by the native catalog query.

    """
    catalog_invocations.append(None)
    return native_paths()
