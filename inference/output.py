# Copyright (c) 2026 Zhambyl Yermagambet
"""Read a structured title from provider terminal output."""

from __future__ import annotations

import re

from pydantic import TypeAdapter, ValidationError

from inference.output_decoders import claude_title, codex_title, direct_title
from inference.provider_errors import (
    ProviderAvailabilityError,
    ProviderTitleMissingError,
    ProviderTitleShapeError,
)

UNAVAILABLE_MARKERS = (
    "rate limit",
    "rate_limit",
    "usage limit",
    "quota",
    "model is not available",
    "model unavailable",
    "authentication_error",
    "not logged in",
)
ESCAPED_TITLE = re.compile(r'\\?"title\\?"\s*:\s*\\?"((?:\\.|[^"\\])*)\\?"')
MINIMUM_TITLE_WORDS = 3


def title_from_output(output: str) -> str:
    """Return a valid title from one provider output stream.

    Returns:
        A valid title from one provider output stream.

    Raises:
        ProviderAvailabilityError: If a provider is not available.
        ProviderTitleMissingError: If a provider has no title.
        ProviderTitleShapeError: If a provider title has an invalid shape.

    """
    title, invalid_shape = _document_title(output)
    if title:
        return title
    escaped_title = _escaped_title(output)
    if escaped_title:
        if _has_requested_title_shape(escaped_title):
            return escaped_title
        invalid_shape = True
    lowered_output = output.lower()
    if any(marker in lowered_output for marker in UNAVAILABLE_MARKERS):
        raise ProviderAvailabilityError
    if invalid_shape:
        raise ProviderTitleShapeError
    raise ProviderTitleMissingError


def _document_title(output: str) -> tuple[str | None, bool]:
    invalid_shape = False
    for candidate in _document_candidates(output):
        title = _title_from_document(candidate)
        if not title:
            continue
        if _has_requested_title_shape(title):
            return title, invalid_shape
        invalid_shape = True
    return None, invalid_shape


def _document_candidates(output: str) -> tuple[str, ...]:
    lines = output.splitlines()
    return *reversed(lines), "".join(lines)


def _title_from_document(document_text: str) -> str | None:
    title = direct_title(document_text)
    if title:
        return title
    title = codex_title(document_text)
    if title:
        return title
    return claude_title(document_text)


def _escaped_title(output: str) -> str | None:
    match = ESCAPED_TITLE.search(output)
    if match is None:
        return None
    try:
        return TypeAdapter(str).validate_json(f'"{match.group(1)}"')
    except ValidationError:
        return None


def _has_requested_title_shape(title: str) -> bool:
    return len(title.split()) >= MINIMUM_TITLE_WORDS
