# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide test architecture protocols."""

from __future__ import annotations

from tests import (
    architecture_project_dependencies as project_dependencies,
    architecture_standard_dependencies as standard_dependencies,
    architecture_test_adapters,
    architecture_test_harnesses,
    architecture_test_protocols,
)

ROOT = project_dependencies.Path(__file__).resolve().parents[1]
MINIMUM_CONTROL_REGISTRATION_COUNT = 20
TEXT_ENCODING = "utf-8"
DOMAIN_PACKAGE = "domain"
IDS_FILE_NAME = "ids.py"
PROTOCOL_DECLARATION_EXEMPTIONS = architecture_test_protocols.PROTOCOL_DECLARATION_EXEMPTIONS


def test_protocol_impls_declare_protocol_they() -> None:
    """Verify protocol implementations declare the protocol they implement."""
    protocols, classes = architecture_test_adapters.protocols_and_classes()
    undeclared = [
        problem
        for description in classes
        if (problem := architecture_test_protocols.undeclared_protocol(description, protocols)) is not None
    ]
    assert not undeclared


def test_declared_protocol_impl_matches_protocol() -> None:
    """Verify each declared protocol implementation has the same methods."""
    protocols, classes = architecture_test_adapters.protocols_and_classes()
    divergent = [
        problem
        for description in classes
        for problem in architecture_test_adapters.protocol_divergences(description, protocols)
    ]
    assert not divergent


def test_protocol_declaration_exemptions_are_all() -> None:
    """Verify each protocol declaration exemption is still in use."""
    protocols, classes = architecture_test_adapters.protocols_and_classes()
    live = architecture_test_protocols.live_protocol_declarations(protocols, classes)
    assert not sorted(set(PROTOCOL_DECLARATION_EXEMPTIONS) - live)


def test_every_registered_control_handler() -> None:
    """Verify every registered control handler declares the protocol."""
    registrations = list(architecture_test_adapters.registered_handlers())
    wrong = [
        problem
        for registration in registrations
        if (problem := architecture_test_harnesses.registration_problem(registration)) is not None
    ]
    assert not wrong
    assert len(registrations) > MINIMUM_CONTROL_REGISTRATION_COUNT


def test_every_registered_control_name_is_real() -> None:
    """Verify every registered control name is a real one."""
    names = architecture_test_adapters.control_names()
    unknown = [
        problem
        for registration in architecture_test_adapters.registered_handlers()
        if (problem := architecture_test_harnesses.unknown_control_problem(registration, names)) is not None
    ]
    assert not unknown


def test_shared_models_do_not_expose_adapter() -> None:
    """Vendor handles stay behind their adapter boundary.

    A session is canonically identified by SessionId, and a model fact carries
    a portable name. Reintroducing a second harness/native/selection identity
    here would make every adapter pretend to support another adapter's concept.
    """
    references = standard_dependencies.importlib.import_module("domain.references")
    session_models = standard_dependencies.importlib.import_module("harness.models.session")
    assert set(session_models.Session.__dataclass_fields__) == {
        "session_id",
        "lead_actor_id",
        "source_reference",
        "working_directory",
        "terminal_window_id",
        "harness_process_id",
        "plugin",
        "project_directory",
    }
    assert set(references.ModelReference.__dataclass_fields__) == {"name", "display_name"}


def test_adapter_identity_types_do_not_live() -> None:
    """Verify adapter identity types do not live in domain identifiers."""
    source = (ROOT / DOMAIN_PACKAGE / IDS_FILE_NAME).read_text(encoding=TEXT_ENCODING)
    forbidden = ("HarnessSessionId", "ModelId", "SelectionId", "ShellNativeId", "CallId")
    assert not any(name in source for name in forbidden)
