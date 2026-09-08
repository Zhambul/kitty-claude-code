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

import re
from typing import TYPE_CHECKING

from tests.canonical_naming_banned_values import (
    BANNED_IDENTIFIERS,
    BANNED_WORDS,
    _banned_word_pattern,
)
from tests.canonical_naming_paths import ROOT, TEXT_ENCODING

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator


def _text_name_violations(
    path: pathlib.Path,
    name: str,
    pattern: re.Pattern[str],
) -> Iterator[str]:
    relative_path = path.relative_to(ROOT)
    if pattern.search(path.name):
        yield f"{relative_path} — file name contains {name!r}"
    for line_number, line in enumerate(path.read_text(encoding=TEXT_ENCODING).splitlines(), 1):
        # This is a vendor field name. Renaming it would stop source decoding.
        if (
            relative_path.as_posix() == "harness/impl/codex/canonical/record_session_sources.py"
            and line.strip() == 'validation_alias="provenance",'
        ):
            continue
        if pattern.search(line):
            yield f"{relative_path}:{line_number}: {name!r}"


def _banned_word_violations(path: pathlib.Path) -> Iterator[str]:
    for word in BANNED_WORDS:
        yield from _text_name_violations(path, word, _banned_word_pattern(word))


def _banned_identifier_violations(path: pathlib.Path) -> Iterator[str]:
    for name in BANNED_IDENTIFIERS:
        pattern = re.compile(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])")
        yield from _text_name_violations(path, name, pattern)
