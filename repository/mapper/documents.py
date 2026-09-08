# Copyright (c) 2026 Zhambyl Yermagambet
"""Describe the documents module.

Any dataclass or pydantic model of ours, as the bytes it is stored or
carried as, and back.

Not only the canonical fact: the engine's own raw events — an output chunk, a
process exit, an interrupt mark — are documents too. They used to be a dict
literal at the writer and a field-by-field read at the translator, twice per
document, with nothing holding the two halves together.
"""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Any, cast

from pydantic import TypeAdapter, ValidationError

if TYPE_CHECKING:
    from collections.abc import Hashable


class StoredDocumentError(ValueError):
    """Represent stored document error.

    A stored document does not match the shape it claims, in either
        direction: an encode that fails validation, or a decode of bytes that were
        never a valid instance of the shape asked for.
    """


@cache
def _adapter(shape: Hashable) -> TypeAdapter[Any]:
    """Build one adapter for each stored document type.

    Returns:
        The type adapter.

    """
    return TypeAdapter(cast("Any", shape))


def encode_document[DocumentT](document: DocumentT) -> bytes:
    """Encode document.

    The document runtime type is the shape to validate and dump against.
        the whole reason this takes a type parameter instead of `object`: the
        adapter it builds is for exactly the caller's type, not a generic one.

    Returns:
        Byte data.

    """
    adapter = _adapter(cast("Hashable", type(document)))
    return adapter.dump_json(document)


def decode_document[DocumentT](shape: type[DocumentT], encoded: bytes | str) -> DocumentT:
    """Decode document.

    The inverse, against the shape the caller expects.

    Returns:
        The document type.

    Raises:
        StoredDocumentError: If a stored document is not valid.

    """
    adapter = _adapter(cast("Hashable", shape))
    try:
        return cast("DocumentT", adapter.validate_json(encoded))
    except ValidationError as error:
        message = f"not a {shape.__name__}: {error}"
        raise StoredDocumentError(message) from error
