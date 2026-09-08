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
import re
from typing import TypeGuard

from tests.canonical_naming_paths import TEXT_ENCODING, _module_paths


def _snake(name: str) -> str:
    return re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name.lstrip("_")).lower()


def _project_classes() -> set[str]:
    classes = set()
    for path in _module_paths():
        tree = ast.parse(path.read_text(encoding=TEXT_ENCODING))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)
    return classes


def _simple_annotation_name(annotation: ast.expr | None) -> str | None:
    """`X` or `X | None` gives "X"; anything else gives None.

    Unions of two real classes, generics and subscripts carry no single class
    to name a parameter after, so the gates skip them.

    Returns:
        The simple class name, the string None, or None for an unsupported annotation.

    """
    if isinstance(annotation, ast.Name):
        return annotation.id
    if isinstance(annotation, ast.Constant) and annotation.value is None:
        return "None"
    return _simple_union_annotation_name(annotation)


def _simple_union_annotation_name(annotation: ast.expr | None) -> str | None:
    """Return the one class name in a simple optional annotation.

    Returns:
        The one class name in a simple optional annotation.

    """
    if not isinstance(annotation, ast.BinOp):
        return None
    if not isinstance(annotation.op, ast.BitOr):
        return None
    names = (
        _simple_annotation_name(annotation.left),
        _simple_annotation_name(annotation.right),
    )
    return _single_class_name(names)


def _single_class_name(names: tuple[str | None, str | None]) -> str | None:
    """Return one non-None class name, if exactly one is present.

    Returns:
        One non-None class name, if exactly one is present.

    """
    class_names: list[str] = [name for name in names if _is_class_name(name)]
    if len(class_names) != 1:
        return None
    return class_names[0]


def _is_class_name(name: str | None) -> TypeGuard[str]:
    """Return whether a simple annotation name is a class name.

    Returns:
        Whether a simple annotation name is a class name.

    """
    return name is not None and name != "None"
