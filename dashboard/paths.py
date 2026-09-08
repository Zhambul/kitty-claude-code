# Copyright (c) 2026 Zhambyl Yermagambet
"""Filesystem locations the dashboard owns.

The directories themselves belong to `core/data.py` — the one owner of where
our files live, and now of the three database paths too. What is left here is
the uploads directory: the one place the dashboard writes bytes rather than
rows, because an attachment reaches the harness as an `@path`.

Answered at CALL time, not at import. `UPLOADS_DIRECTORY` used to be a module
constant computed when this file was first imported, which made it a global with
one owner and many patchers: the test suite had to substitute the attribute to
keep a run out of your real data directory. It hangs off `core/data.py`'s answer
now, so the environment is the only knob and there is nothing to rebind.
"""

from __future__ import annotations

import re
from pathlib import Path

from core.clients import REPOSITORY_ROOT
from core.data import data_directory
from domain.ids import SessionId

# The daemon re-spawns itself through `bin/`. The root it hangs off is resolved
# once, in core/clients.py, from a package's own location — this module used to
# count two directories up from itself, which is the mistake that once killed
# every pane process on startup.
BIN_DIRECTORY = str(REPOSITORY_ROOT / "bin")


def uploads_directory() -> str:
    """Return the uploads directory.

    The one place the dashboard writes bytes rather than rows.

    Returns:
        Uploads directory.

    """
    return str(Path(data_directory()) / "uploads")


def safe_session_name(session_id: SessionId) -> str:
    """Return the safe session name.

    Returns:
        Safe session name.

    """
    return re.sub(r"[^A-Za-z0-9._-]", "-", session_id)


def session_uploads_directory(session_id: SessionId) -> str:
    """Return the session uploads directory.

    Returns:
        Session uploads directory.

    """
    name = safe_session_name(SessionId(session_id.strip())) or "staging"
    return str(Path(uploads_directory()) / name)
