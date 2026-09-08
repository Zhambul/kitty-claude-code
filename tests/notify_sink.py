#!/usr/bin/env python3
# Copyright (c) 2026 Zhambyl Yermagambet
"""Describe the notify sink module.

The suite's stand-in for the `notify` skill script (docs/testing.md,
*Hermeticity*).

`dashboard/notify/channels.py` degrades to spawning `config.NOTIFY_CMD` — by
default the developer's REAL `~/.claude/skills/notify/scripts/notify.py`, i.e.
their actual Telegram bot — whenever the Bot API credentials are unconfigured.
The hermetic fixture makes them unconfigured ON PURPOSE, so every test that
drives a red/green transition through an un-stubbed `Notifier` used to deliver a
real alert to the developer's phone. conftest aims the knob here instead.

Deliberately a no-op: the point is that the argv never leaves the machine. Set
BAQYLAU_NOTIFY_SINK_LOG to keep a record when debugging what the suite would
have sent.
"""

import os
import pathlib
import sys


def main() -> int:
    """Record notification arguments locally when a log path is configured.

    Returns:
        Zero after processing the arguments without sending a notification.

    """
    log = os.environ.get("BAQYLAU_NOTIFY_SINK_LOG")
    if log:
        with pathlib.Path(log).open("a", encoding="utf-8") as log_file:
            rendered_arguments = "\t".join(sys.argv[1:]).replace("\n", r"\n")
            log_file.write(f"{rendered_arguments}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
