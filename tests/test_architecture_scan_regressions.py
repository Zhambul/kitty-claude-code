# Copyright (c) 2026 Zhambyl Yermagambet
"""Keep architecture checks effective after module splits."""

import ast
from pathlib import Path

import pytest

from tests import (
    architecture_test_inheritance as inheritance,
    architecture_test_json as file_checks,
    architecture_test_registrations as registrations,
    architecture_test_symbols as symbols,
)
from tests.architecture_test_syntax import ClassDescription

READ_METHOD = "read"
SELF_PARAMETER = "self"
TEXT_ENCODING = "utf-8"
ROOT_ATTRIBUTE = "ROOT"


def test_inheritance_keeps_concrete_override() -> None:
    """Check inherited declarations and an incompatible override."""
    base = ClassDescription("base.py:1", "Base", ["Reader"], {READ_METHOD: (SELF_PARAMETER, "after")})
    child = ClassDescription("child.py:1", "Child", ["Base"], {READ_METHOD: (SELF_PARAMETER, "wrong")})
    resolved = inheritance.inherited_description(child, {"Base": base})
    assert "Reader" in resolved.bases
    assert resolved.members[READ_METHOD] == (SELF_PARAMETER, "wrong")


def test_protocol_stubs_are_not_implementations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Accept a default method but keep a missing implementation visible."""
    path = tmp_path / "reader.py"
    path.write_text(
        "class Reader:\n    def watch(self):\n        return ()\n    def read(self, after):\n        ...\n",
        encoding=TEXT_ENCODING,
    )
    monkeypatch.setattr(inheritance, ROOT_ATTRIBUTE, tmp_path)
    description = ClassDescription(
        "reader.py:1", "Reader", [], {"watch": (SELF_PARAMETER,), READ_METHOD: (SELF_PARAMETER, "after")},
    )
    assert inheritance.protocol_defaults(description).members == {"watch": (SELF_PARAMETER,)}


def test_imported_mapping_reports_wrong_bases(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Follow imports and mapping expansion without hiding a wrong base."""
    monkeypatch.setattr(symbols, ROOT_ATTRIBUTE, tmp_path)
    monkeypatch.setattr(registrations, ROOT_ATTRIBUTE, tmp_path)
    (tmp_path / "handlers.py").write_text(
        "class BadHandler: pass\nHANDLERS = MappingProxyType({'send_text': BadHandler()})\n",
        encoding=TEXT_ENCODING,
    )
    path = tmp_path / "controller.py"
    path.write_text("from handlers import HANDLERS\nCURRENT = {**HANDLERS}\n", encoding=TEXT_ENCODING)
    found = list(registrations.registrations(path, ast.Name(id="CURRENT"), {}))
    assert len(found) == 1
    assert found[0][1:] == ("send_text", "BadHandler", [])


def test_screen_read_does_not_hide_a_file_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ignore a terminal screen read but still detect a file read beside it."""
    monkeypatch.setattr(file_checks, ROOT_ATTRIBUTE, tmp_path)
    path = tmp_path / "reader.py"
    path.write_text("screen_driver.read_text(window_id)\npath.read_text()\n", encoding=TEXT_ENCODING)
    assert list(file_checks.file_access_violations(path, (r"\.read_text\(",)))
    path.write_text("screen_driver.read_text(window_id)\n", encoding=TEXT_ENCODING)
    assert not list(file_checks.file_access_violations(path, (r"\.read_text\(",)))
