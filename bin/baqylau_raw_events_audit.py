#!/Users/z.yermagambet/code/personal/baqylau/.venv/bin/python
# Copyright (c) 2026 Zhambyl Yermagambet
"""Inspect raw harness events and their canonical interpretations."""

import sys
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1]),
)

from app.raw_events_audit_cli import main

if __name__ == "__main__":
    sys.exit(main())
