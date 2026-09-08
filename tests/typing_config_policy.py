# Copyright (c) 2026 Zhambyl Yermagambet
"""Configuration policy for static type checks."""

from __future__ import annotations

import configparser
import subprocess  # noqa: S404 -- Run the installed type checker with a temporary test configuration.
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_ENCODING = "utf-8"


def is_type_exempt_section(parser: configparser.ConfigParser, section: str) -> bool:
    """Return whether a Mypy section disables typed definitions.

    Returns:
        Whether a Mypy section disables typed definitions.

    """
    if not section.startswith("mypy-"):
        return False
    return parser.get(section, "disallow_untyped_defs", fallback="True") == "False"


def mypy_exempt_packages() -> set[str]:
    """Return packages that Mypy does not require annotations from.

    Returns:
        Packages that Mypy does not require annotations from.

    """
    parser = configparser.ConfigParser()
    parser.read(ROOT / "mypy.ini", encoding=TEXT_ENCODING)
    exempt = set()
    for section in parser.sections():
        if not is_type_exempt_section(parser, section):
            continue
        for pattern in section[len("mypy-") :].split(","):
            package = pattern.strip().removesuffix(".*")
            if package:
                exempt.add(package)
    return exempt


def ruff_annotation_exemptions() -> dict[str, list[str]]:
    """Return Ruff file rules that disable annotation checks.

    Returns:
        Ruff file rules that disable annotation checks.

    """
    config = tomllib.loads((ROOT / "ruff.toml").read_text(encoding=TEXT_ENCODING))
    per_file_rules = config["lint"].get("per-file-ignores", {})
    return {
        file_pattern: codes
        for file_pattern, codes in per_file_rules.items()
        if any(code == "ANN" or code.startswith("ANN") for code in codes)
    }


def package_needs_type_exemption(package: str) -> bool:
    """Return whether one package still needs its Mypy exemption.

    Returns:
        Whether one package still needs its Mypy exemption.

    """
    parser = configparser.ConfigParser()
    parser.read(ROOT / "mypy.ini", encoding=TEXT_ENCODING)
    parser.remove_section(f"mypy-{package}.*")
    with tempfile.NamedTemporaryFile("w", suffix=".ini", dir=ROOT, encoding=TEXT_ENCODING) as config_file:
        parser.write(config_file)
        config_file.flush()
        completed = subprocess.run(  # noqa: S603 -- Use this Python executable with fixed mypy options, without a shell.
            [sys.executable, "-m", "mypy", "--no-incremental", "--config-file", config_file.name, package],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
        )
    return completed.returncode != 0
