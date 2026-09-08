# Copyright (c) 2026 Zhambyl Yermagambet
"""Regular expressions and markers for Codex item parsing."""

import re

EXECUTION_EXIT_PATTERN = re.compile(r"(?:^|\n)(?:Exit code|Process exited with code)[: ]+(\d+)")
EXECUTION_EXIT_SCAN_BYTES = 300
CITATION_PATTERN = re.compile(r"cite[^]+\s*")
UPDATE_PLAN_TOOL_NAME = "update_plan"
JAVASCRIPT_COMMAND_PATTERN = re.compile(
    r"[\"']?cmd[\"']?\s*:\s*"
    r"(\[[^\]]*\]|\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|`(?:[^`\\]|\\.)*`)",
)
OUTPUT_MARKER = "Output:\n"
JAVASCRIPT_TOOL_PATTERN = re.compile(r"tools\.([A-Za-z_][A-Za-z0-9_]*)\s*\(")
COLLABORATION_TOOL_PREFIX = re.compile(r"^multi_agent_v\d+__")
JAVASCRIPT_QUOTES = "\"'`"
PLAN_STEP_PATTERN = re.compile(
    r"[\"']?step[\"']?\s*:\s*"
    r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')",
)
PLAN_STATUS_PATTERN = re.compile(
    r"[\"']?status[\"']?\s*:\s*"
    r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')",
)
