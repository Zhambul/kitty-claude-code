# Copyright (c) 2026 Zhambyl Yermagambet
"""Own type-hint values and provider extraction for dependency resolution."""

from collections.abc import Callable
from typing import Annotated, Any, get_args, get_origin

from fastapi.params import Depends

from app.injection_errors import MissingProviderDependencyError


class TypeHint:
    """Represent one provider parameter type hint.

    Python can supply a class, union, generic alias, or annotated wrapper.
    This name makes the reflection boundary explicit.
    """


def provider_from_hint(name: str, type_hint: TypeHint | None) -> Callable[..., Any]:
    """Return the provider declared by one annotated parameter.

    Returns:
        The provider declared by one annotated parameter.

    Raises:
        MissingProviderDependencyError: If the parameter has no provider.

    """
    if get_origin(type_hint) is Annotated:
        for metadata in get_args(type_hint)[1:]:
            if isinstance(metadata, Depends) and metadata.dependency is not None:
                return metadata.dependency
    raise MissingProviderDependencyError(name, type_hint)
