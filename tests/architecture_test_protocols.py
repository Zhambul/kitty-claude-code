# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide architecture test protocols."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
)

# Keep dependency modules separate from test helpers.
# isort: split

from tests import (
    architecture_packages,
    architecture_test_canonical,
    architecture_test_databases,
    architecture_test_declarations,
    architecture_test_json,
    architecture_test_syntax,
    architecture_test_tables,
    architecture_test_terminals,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
TEXT_ENCODING = "utf-8"
PYTHON_FILE_PATTERN = "*.py"
DOMAIN_PACKAGE = "domain"
CODEX_PACKAGE = "codex"
IDS_FILE_NAME = "ids.py"
type MethodSignatures = dict[str, tuple[str, ...]]
OUR_PACKAGES = architecture_packages.owned_packages()
PROTOCOL_DECLARATION_EXEMPTIONS = project_dependencies.MappingProxyType({
    ("TerminalInputService", "TerminalSessionReader"): "the Protocol lives in dashboard/, which app/ may not import",
})


def concrete_vocabulary_violations() -> list[str]:
    """Check shared source files for concrete harness vocabulary.

    Returns:
        Messages with each file and its prohibited words.

    """
    violations: list[str] = []
    for path in architecture_test_databases.paths_under(architecture_test_json.canonical_vocabulary_paths()):
        if path == ROOT / DOMAIN_PACKAGE / IDS_FILE_NAME:
            continue
        lowered = path.read_text(encoding=TEXT_ENCODING).lower()
        words = [
            word
            for word in ("claude", CODEX_PACKAGE, "anthropic", "openai", "rollout", "transcript")
            if word in lowered
        ]
        if words:
            violations.append(architecture_test_syntax.contains_message(path.relative_to(ROOT), words))
    return violations


def repository_builders() -> set[str]:
    """Find repository implementation imports outside the repository package.

    Returns:
        The relative paths of the importing source files.

    """
    builders = set()
    for package in OUR_PACKAGES:
        for path, imported in architecture_test_terminals.imports_under(package):
            relative_path = path.relative_to(ROOT).as_posix()
            if not relative_path.startswith("repository/") and imported.startswith("repository.impl"):
                builders.add(relative_path)
    return builders


def audit_floor_importers() -> set[str]:
    """Return modules that import the audit-record floor.

    Returns:
        Modules that import the audit-record floor.

    """
    importers = set()
    for package in OUR_PACKAGES:
        for path in sorted((ROOT / package).rglob(PYTHON_FILE_PATTERN)):
            importer = architecture_test_json.audit_floor_importer(path)
            if importer is not None:
                importers.add(importer)
    return importers


def classes_in_path(
    path: project_dependencies.Path,
) -> project_dependencies.Iterator[tuple[bool, architecture_test_syntax.ClassDescription]]:
    """Read class declarations from one Python file.

    Yields:
        A protocol flag and class description for each declaration.

    """
    tree = architecture_test_declarations.parse_python_source(path)
    for node in standard_dependencies.ast.walk(tree):
        if not isinstance(node, standard_dependencies.ast.ClassDef):
            continue
        bases = [
            standard_dependencies.ast.unparse(base).rsplit(".", 1)[-1]
            for base in node.bases
        ]
        is_protocol = architecture_test_canonical.is_protocol(bases)
        yield (
            is_protocol,
            architecture_test_syntax.ClassDescription(
                where=f"{path.relative_to(ROOT)}:{node.lineno}",
                name=node.name,
                bases=bases,
                members=architecture_test_tables.method_signatures(node),
            ),
        )


def undeclared_protocol(
    description: architecture_test_syntax.ClassDescription,
    protocols: dict[str, MethodSignatures],
) -> str | None:
    """Check whether a class declares a matching protocol or has an exemption.

    Returns:
        A failure message for an undeclared match, or None if permitted.

    """
    matched = architecture_test_canonical.matched_protocols(description, protocols)
    if not matched or any(protocol in description.bases for protocol in matched):
        return None
    if all((description.name, protocol) in PROTOCOL_DECLARATION_EXEMPTIONS for protocol in matched):
        return None
    protocol_names = "/".join(sorted(matched))
    return f"{description.where} {description.name} implements {protocol_names} without saying so"


def protocol_member_divergences(
    description: architecture_test_syntax.ClassDescription,
    protocol: str,
    signature: MethodSignatures,
) -> project_dependencies.Iterator[str]:
    """Compare class members with a protocol signature.

    Yields:
        Each member difference reported by the signature check.

    """
    for member, arguments in sorted(signature.items()):
        divergence = architecture_test_canonical.protocol_member_divergence(description, protocol, member, arguments)
        if divergence is not None:
            yield divergence


def live_protocol_declarations(
    protocols: dict[str, MethodSignatures],
    classes: list[architecture_test_syntax.ClassDescription],
) -> set[tuple[str, str]]:
    """Find all current class and matching protocol pairs.

    Returns:
        The class-name and protocol-name pairs with matching signatures.

    """
    live: set[tuple[str, str]] = set()
    for description in classes:
        live.update(
            (description.name, protocol)
            for protocol in architecture_test_canonical.matched_protocols(description, protocols)
        )
    return live
