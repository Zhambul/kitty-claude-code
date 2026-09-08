# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test canonical."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_syntax,
    architecture_test_tables,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
type MethodSignatures = dict[str, tuple[str, ...]]


def foreground_hook_violations(
    path: project_dependencies.Path,
    forbidden_roots: set[str],
) -> project_dependencies.Iterator[str]:
    """Check a foreground hook for prohibited imports and legacy names.

    Yields:
        Messages with the source path and each prohibited reference.

    """
    for _imported_path, imported in architecture_test_syntax.imports_under_path(path):
        if imported.split(".", 1)[0] in forbidden_roots:
            yield f"{path.relative_to(ROOT)} imports {imported}"
    source = path.read_text(encoding=TEXT_ENCODING)
    yield from (
        f"{path.relative_to(ROOT)} contains {forbidden_name}"
        for forbidden_name in ("core.ops", "core.state", "hand_put", "fg-live", "spawn_streamer", "claude-stream.py")
        if forbidden_name in source
    )


def consumer_source_violations(
    consumer: project_dependencies.Path,
    forbidden_fragments: tuple[str, ...],
) -> project_dependencies.Iterator[str]:
    """Check a consumer file or package for prohibited source fragments.

    Yields:
        A message with each file and its matching fragments.

    """
    paths = sorted(consumer.rglob(PYTHON_FILE_PATTERN)) if consumer.is_dir() else (consumer,)
    for path in paths:
        source = path.read_text(encoding=TEXT_ENCODING)
        found_fragments = [fragment for fragment in forbidden_fragments if fragment in source]
        if found_fragments:
            yield architecture_test_syntax.contains_message(path.relative_to(ROOT), found_fragments)


def collect_protocol_or_class(
    description: architecture_test_syntax.ClassDescription,
    protocols: dict[str, MethodSignatures],
    classes: list[architecture_test_syntax.ClassDescription],
    *,
    is_protocol: bool,
) -> None:
    """Store one protocol or concrete class description."""
    if not is_protocol:
        classes.append(description)
    elif not description.name.startswith("_"):
        protocols[description.name] = description.members


def is_protocol(bases: list[str]) -> bool:
    """Check class bases for a protocol declaration.

    Returns:
        True for a direct, parameterized, or qualified protocol base.

    """
    if "Protocol" in bases:
        return True
    return architecture_test_tables.has_generic_protocol_base(bases)


def matched_protocols(
    description: architecture_test_syntax.ClassDescription,
    protocols: dict[str, MethodSignatures],
) -> list[str]:
    """Find protocols whose method signatures match a class.

    Returns:
        The names of all matching protocols.

    """
    return [
        protocol
        for protocol, signature in protocols.items()
        if architecture_test_tables.satisfies(description.members, signature)
    ]


def protocol_member_divergence(
    description: architecture_test_syntax.ClassDescription,
    protocol: str,
    member: str,
    arguments: tuple[str, ...],
) -> str | None:
    """Return a signature mismatch for one protocol member.

    Returns:
        A signature mismatch for one protocol member.

    """
    actual_arguments = description.members.get(member)
    if actual_arguments is None:
        return f"{description.where} {description.name} declares {protocol} but never defines {member}()"
    if actual_arguments != arguments:
        return (
            f"{description.where} {description.name}.{member}{actual_arguments} "
            f"does not match {protocol}.{member}{arguments}"
        )
    return None


def control_members(control_class: standard_dependencies.ast.ClassDef) -> dict[str, str]:
    """Read string-valued members from a control class.

    Returns:
        Each member name and its assigned string value.

    """
    member_values: dict[str, str] = {}
    for statement in control_class.body:
        member = architecture_test_tables.control_member_value(statement)
        if member is not None:
            member_name, member_value = member
            member_values[member_name] = member_value
    return member_values
