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

from tests.canonical_naming_paths import PACKAGES, ROOT, _package_paths

if TYPE_CHECKING:
    import pathlib

BANNED_WORDS = ("envelope", "evidence", "wire", "wiring", "provenance")

# Classes the owner decided should never exist: one canonical event class,
# `domain.events.CanonicalEvent`, end to end. A second one always meant to grow
# back into a stored-document type this tree no longer has. Grow-only, like
# the word list above.


BANNED_IDENTIFIERS = ("StoredCanonicalEvent", "CommittedEvent", "CanonicalEventDocument")

# Scanned wider than the two naming gates above: `bin/` and `client/` carry
# prose and identifiers too, and the browser half of this codebase is JS, not
# Python.


BANNED_WORD_PACKAGES = (*PACKAGES, "bin", "client")


def _banned_word_pattern(word: str) -> re.Pattern[str]:
    # Underscore is deliberately NOT a boundary character: `client/_wire.py`
    # and `_ENVELOPE_TS` must be caught exactly like the plain word in prose.
    return re.compile(rf"(?<![A-Za-z0-9]){re.escape(word)}(?![A-Za-z0-9])", re.IGNORECASE)


def _banned_word_files() -> list[pathlib.Path]:
    paths = _package_paths(BANNED_WORD_PACKAGES)
    paths.extend(sorted((ROOT / "dashboard" / "static").glob("*.js")))
    return paths
