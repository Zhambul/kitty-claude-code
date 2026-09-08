# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that check deterministic file fixtures."""

from __future__ import annotations

from pathlib import Path

from pytest_bdd import given, parsers, then


@given("the file operation fixture does not exist")
def file_operation_fixture_does_not_exist(file_operation_path: str) -> None:
    """Verify the file-operation fixture does not exist."""
    assert not Path(file_operation_path).exists()


@given("the file rename fixtures do not exist")
def file_rename_fixtures_do_not_exist(file_rename_paths: tuple[str, str]) -> None:
    """Verify the file-rename fixtures do not exist."""
    present = [path for path in file_rename_paths if Path(path).exists()]
    assert not present, f"file rename fixtures exist: {present}"


@given("the missing file fixture does not exist")
def missing_file_fixture_does_not_exist(missing_file_path: str) -> None:
    """Verify the missing-file fixture does not exist."""
    assert not Path(missing_file_path).exists()


@given(parsers.parse("the rewind file contains '{text}'"))
def rewind_file_has_initial_content(rewind_file_path: str, text: str) -> None:
    """Verify initial rewind-file content."""
    assert Path(rewind_file_path).read_text(encoding="utf-8").strip() == text


@then("the file operation fixture is absent")
def file_operation_fixture_is_absent(file_operation_path: str) -> None:
    """Verify the file-operation fixture is absent."""
    assert not Path(file_operation_path).exists()


@then(parsers.parse("the file operation fixture contains '{text}'"))
def file_operation_fixture_contains(file_operation_path: str, text: str) -> None:
    """Verify file-operation fixture content."""
    content = Path(file_operation_path).read_text(encoding="utf-8")
    assert text in content, f"file operation fixture does not contain {text!r}: {content!r}"


@then(parsers.parse("the rewind file contains exactly '{text}'"))
def rewind_file_contains_exactly(rewind_file_path: str, text: str) -> None:
    """Verify complete rewind-file content."""
    content = Path(rewind_file_path).read_text(encoding="utf-8").strip()
    assert content == text, f"rewind file contains {content!r}"
