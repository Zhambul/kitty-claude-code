# Copyright (c) 2026 Zhambyl Yermagambet
"""Read and write terminal handoff documents."""

from __future__ import annotations

import contextlib
import os
import pathlib

from pydantic import BaseModel, ValidationError


def read_document[DocumentT: BaseModel](path: str, model: type[DocumentT]) -> DocumentT | None:
    """Read one valid document, or return nothing.

    Returns:
        The validated document, or None if reading or validation fails.

    """
    try:
        return model.model_validate_json(pathlib.Path(path).read_bytes())
    except (OSError, ValidationError):
        return None


def write_document(path: str, document: BaseModel) -> None:
    """Write one document with an atomic replace."""
    temporary_path = f"{path}.{os.getpid()}.tmp"
    try:
        _replace_document(temporary_path, path, document)
    except OSError:
        with contextlib.suppress(OSError):
            pathlib.Path(temporary_path).unlink()


def _replace_document(temporary_path: str, path: str, document: BaseModel) -> None:
    pathlib.Path(temporary_path).write_text(document.model_dump_json(), encoding="utf-8")
    pathlib.Path(temporary_path).replace(path)
