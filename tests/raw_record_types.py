# Copyright (c) 2026 Zhambyl Yermagambet
"""Shared types for raw-record architecture checks."""

from __future__ import annotations

import ast
from dataclasses import dataclass

SEQUENCE_TYPES = frozenset((
    "Collection",
    "Deque",
    "FrozenSet",
    "Generator",
    "Iterable",
    "Iterator",
    "List",
    "Sequence",
    "Set",
    "Tuple",
    "deque",
    "frozenset",
    "list",
    "set",
    "tuple",
))
TUPLE_TYPES = frozenset(("Tuple", "tuple"))
EMPTY_RESOLUTION_PATH: frozenset[str] = frozenset()
type Violation = tuple[int, str, str]


@dataclass(frozen=True)
class ModuleTypes:
    """Store aliases and imported sequence names for one module."""

    aliases: dict[str, ast.expr]
    sequence_names: dict[str, str]
