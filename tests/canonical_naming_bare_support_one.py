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
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import TypeGuard


def _is_bare_str(annotation: ast.expr | None) -> bool:
    """Return whether an annotation contains a bare string type.

    Returns:
        Whether an annotation contains a bare string type.

    """
    annotation_nodes = [annotation]
    while annotation_nodes:
        current_annotation = annotation_nodes.pop()
        if _is_bare_string_annotation(current_annotation):
            return True
        if _is_bit_or_union_annotation(current_annotation):
            annotation_nodes.extend((current_annotation.left, current_annotation.right))
    return False


def _is_bare_string_annotation(annotation: ast.expr | None) -> bool:
    """Return whether an annotation is the bare string type.

    Returns:
        Whether an annotation is the bare string type.

    """
    if not isinstance(annotation, ast.Name):
        return False
    return annotation.id == "str"


def _is_bit_or_union_annotation(annotation: ast.expr | None) -> TypeGuard[ast.BinOp]:
    """Return whether an annotation is a bit-or union.

    Returns:
        Whether an annotation is a bit-or union.

    """
    if not isinstance(annotation, ast.BinOp):
        return False
    return isinstance(annotation.op, ast.BitOr)


@dataclass(frozen=True)
class BareStringGate:
    """Define one rule for a named value that cannot use bare strings."""

    packages: tuple[str, ...]
    allowed: tuple[str, ...]
    name_matches: Callable[[str], bool]
    replacement: str


def _annotated_fields(tree: ast.AST) -> Iterator[tuple[ast.ClassDef, ast.AnnAssign, str]]:
    """Read annotated fields from all classes.

    Yields:
        The class node, assignment node, and field name.

    """
    for class_node in ast.walk(tree):
        if isinstance(class_node, ast.ClassDef):
            yield from _class_annotated_fields(class_node)


def _class_annotated_fields(class_node: ast.ClassDef) -> Iterator[tuple[ast.ClassDef, ast.AnnAssign, str]]:
    """Read annotated fields from one class.

    Yields:
        The class node, assignment node, and field name.

    """
    for statement in class_node.body:
        if not isinstance(statement, ast.AnnAssign):
            continue
        if isinstance(statement.target, ast.Name):
            yield class_node, statement, statement.target.id


def _is_gate_violation(
    name: str,
    annotation: ast.expr | None,
    relative_path: str,
    bare_string_gate: BareStringGate,
) -> bool:
    """Return true when one named value violates a bare-string gate.

    Returns:
        True when one named value violates a bare-string gate.

    """
    allowed_key = f"{relative_path}:{name}"
    return (
        bare_string_gate.name_matches(name) and allowed_key not in bare_string_gate.allowed and _is_bare_str(annotation)
    )
