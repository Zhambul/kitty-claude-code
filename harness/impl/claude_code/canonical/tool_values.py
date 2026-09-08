# Copyright (c) 2026 Zhambyl Yermagambet
"""Define shared Claude Code tool values."""

import re

BACKGROUND_LAUNCH_STUB = "Command running in background with ID:"
SHELL_EXIT_CODE = re.compile(r"(?:^|\n)(?:Error: )?Exit code (\d+)(?:\n|$)")
FINISHED_PHASE = "finished"
