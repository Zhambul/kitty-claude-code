# Copyright (c) 2026 Zhambyl Yermagambet
"""Focused canonical naming architecture gate.

Gate 1 — a parameter is named after its class. A parameter whose annotation is
one of OUR classes must carry that class's full name in snake case, either
exactly (`session_repository: SessionRepository`) or as a suffix
(`resume_session_id: SessionId`). A shortened name (`sessions:
SessionRepository`) hides what the object is, and the reader has to open the
class to find out.

Gate 2 — an id is a typed id, never a bare `str`. A parameter or a dataclass
field whose name ends in `_id` must use a NewType from `domain/ids.py` (or a
package's own id type). A bare `str` lets any string flow into any id slot,
and the type checker cannot catch the swap.

Gate 4 (below Gate 3, the banned-words gate) — a harness's name is a typed
`HarnessName`, never a bare `str`, for the same reason as Gate 2: a parameter
or dataclass field named exactly `harness` or ending `_harness` must not be
annotated bare `str`.

Gate 5 (TASKS.md item 4b) — a closed string vocabulary is an enum, never a
bare `Literal["a", "b"]` union or a module-level `frozenset` of string
literals. Every one of OUR verdicts, roles, phases and command sets became a
`StrEnum` (`domain/outcomes.py` and related modules); what is left as a `Literal` union
or a bare-string `frozenset` in the production packages is either a vendor's
own vocabulary (a record's `type`/`kind` tag, read verbatim off foreign JSON —
`records.py` in each harness, `rollout.py`'s `KINDS`, `transcript.py`'s
`RECORD_TYPES`) or another program's own names (`terminal/launch.py`'s
`SUPPORTED_LOGIN_SHELLS`), each judged and commented in place. The allowlist
below is that judgment, one line per exception; it only ever shrinks.

Scope: the production packages. `tests/` is not swept (same ratchet stance as
mypy.ini). `api/` is exempt from Gates 2 and 4 only: the HTTP boundary carries
strings by design, and its mappers are exactly where a typed id or a typed
harness name becomes one.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tests.canonical_naming_paths import PACKAGES, ROOT
from tests.canonical_naming_vocabulary_values import VOCABULARY_GATE_EXEMPT_FILES

if TYPE_CHECKING:
    import pathlib


def _vocabulary_files() -> list[pathlib.Path]:
    paths = []
    for package in PACKAGES:
        paths.extend(_vocabulary_paths(package))
    return paths


def _vocabulary_paths(package: str) -> list[pathlib.Path]:
    """Return vocabulary-gate files from one package.

    Returns:
        Vocabulary-gate files from one package.

    """
    return [
        path for path in sorted((ROOT / package).rglob("*.py"))
        if _is_vocabulary_file(path)
    ]


def _is_vocabulary_file(path: pathlib.Path) -> bool:
    """Return whether a path is checked by the vocabulary gate.

    Returns:
        Whether a path is checked by the vocabulary gate.

    """
    if "__pycache__" in path.parts:
        return False
    return path.relative_to(ROOT).as_posix() not in VOCABULARY_GATE_EXEMPT_FILES


@dataclass(frozen=True)
class ModuleAssignment:
    """Represent one module-level assignment."""

    targets: tuple[ast.expr, ...]
    expression: ast.AST | None
    line_number: int
