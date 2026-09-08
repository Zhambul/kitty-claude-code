#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""Expand or collapse one file in the terminal mirror.

    terminal_view.py baqylau-view://SESSION/KIND/ENTRY

The terminal's open-actions configuration names this file for the `baqylau-view`
protocol, so a click on a file line in the pane lands here.

Nothing is fetched and nothing is stored server-side. A file entry carries its
own diff, so which files are expanded is the PANE's state: this program flips one
entry in a local file and signals the pane to re-read it and repaint
(`client/_handoff.py`). The daemon never knew and no longer needs to.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # my own directory

import _handoff

SCHEME = "baqylau-view://"
VIEW_PATH_COMPONENTS = 3
USAGE = "usage: terminal_view.py baqylau-view://SESSION/KIND/ENTRY"


def main(arguments: list[str]) -> int:
    """Run the command.

    Returns:
        Integer result.

    """
    if len(arguments) != 1 or not arguments[0].startswith(SCHEME):
        sys.stderr.write(f"{USAGE}\n")
        return 2
    parts = arguments[0][len(SCHEME) :].split("/", 2)
    if len(parts) != VIEW_PATH_COMPONENTS:
        sys.stderr.write(f"{USAGE}\n")
        return 2
    session_id, kind, entry_id = parts
    _handoff.toggle(session_id, kind, entry_id)
    # A pane that is not running leaves the toggle recorded and nothing painted,
    # which is the honest outcome: the next pane on this session opens with the
    # reader's own expansions still in place.
    _handoff.wake(session_id, kind)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
