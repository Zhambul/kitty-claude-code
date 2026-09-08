# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed failures from dependency graph resolution."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.injection_types import TypeHint


class MissingProviderDependencyError(TypeError):
    """Report a parameter that does not declare a provider."""

    def __init__(self, name: str, type_hint: TypeHint | None) -> None:
        """Create a failure for one provider parameter."""
        super().__init__(f"parameter {name!r} declares no provider: {type_hint!r}")
