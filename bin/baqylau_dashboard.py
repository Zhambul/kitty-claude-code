#!/Users/z.yermagambet/code/personal/baqylau/.venv/bin/python
# Copyright (c) 2026 Zhambyl Yermagambet
"""Baqylau dashboard process entry."""

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from dashboard import cli

if __name__ == "__main__":
    sys.exit(cli.main(sys.argv))
