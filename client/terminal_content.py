#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""Copy what a mirror block holds to the system clipboard.

    terminal_content.py baqylau-content://SESSION/KIND/TARGET

The terminal's open-actions configuration names this file for the
`baqylau-content` protocol, so a click on a ⧉ link in the pane lands here.

Nothing is fetched. The pane holds every byte it draws — content is embedded in
the entries it was served — so it publishes the text behind its own links to a
local file and this program reads it (`client/_handoff.py`). A daemon that is
down changes nothing about a copy, which is the point: this is a frontend
gesture over data the frontend already has.
"""

from __future__ import annotations

import subprocess  # noqa: S404 -- Copy pane text to the native clipboard program.
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # my own directory

import _handoff

SCHEME = "baqylau-content://"
CONTENT_PATH_COMPONENTS = 3
CLIPBOARD_COMMAND = ("pbcopy",)
USAGE = "usage: terminal_content.py baqylau-content://SESSION/KIND/TARGET"


def main(arguments: list[str]) -> int:
    """Run the command.

    Returns:
        Integer result.

    """
    if len(arguments) != 1 or not arguments[0].startswith(SCHEME):
        sys.stderr.write(f"{USAGE}\n")
        return 2
    parts = arguments[0][len(SCHEME) :].split("/", 2)
    if len(parts) != CONTENT_PATH_COMPONENTS:
        sys.stderr.write(f"{USAGE}\n")
        return 2
    session_id, kind, name = parts
    text = _handoff.target(session_id, kind, name)
    if text is None:
        return 0  # no pane, or a link it no longer draws
    subprocess.run(CLIPBOARD_COMMAND, input=text.encode("utf-8"), check=False)  # noqa: S603 -- The fixed clipboard command receives text only through stdin.
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
