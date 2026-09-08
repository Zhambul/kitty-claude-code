# Copyright (c) 2026 Zhambyl Yermagambet
"""Provider graph resolution context."""

from __future__ import annotations


class ProviderGraphContext:
    """Provide named provider resolution to graph groups."""

    def provider[ProviderValue](self, name: str, expected_type: type[ProviderValue]) -> ProviderValue:
        """Resolve one named provider."""
        raise NotImplementedError
