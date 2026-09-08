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
from typing import TYPE_CHECKING

from tests.canonical_naming_parameter_iteration import annotated_parameters
from tests.canonical_naming_parameter_support_one import _simple_annotation_name, _snake
from tests.canonical_naming_paths import ROOT, TEXT_ENCODING

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator


def _parameter_name_violations(
    path: pathlib.Path,
    classes: set[str],
) -> Iterator[str]:
    tree = ast.parse(path.read_text(encoding=TEXT_ENCODING))
    for function, argument in annotated_parameters(tree):
        violation = _parameter_name_violation(path, function, argument, classes)
        if violation is not None:
            yield violation


def _parameter_name_violation(
    path: pathlib.Path,
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    argument: ast.arg,
    classes: set[str],
) -> str | None:
    """Return the naming violation for one typed parameter.

    Returns:
        The naming violation for one typed parameter.

    """
    class_name = _simple_annotation_name(argument.annotation)
    if class_name not in classes:
        return None
    if class_name == "HarnessName" and argument.arg == "harness":
        return None
    wanted_name = _snake(class_name)
    if argument.arg == wanted_name or argument.arg.endswith(f"_{wanted_name}"):
        return None
    return (
        f"{path.relative_to(ROOT)}:{function.lineno} "
        f"{function.name}({argument.arg}: {class_name}) — name it "
        f"`{wanted_name}` or `<qualifier>_{wanted_name}`"
    )
