# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that define session configurations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import given, parsers

from tests.e2e.testkit import references as refs

if TYPE_CHECKING:
    from tests.e2e.testkit import session_contexts

MODEL_OPTION = "--e2e-model"
EFFORT_OPTION = "--e2e-effort"


def _configured_spec(
    context: session_contexts.SessionConfigContext,
    harness: str,
    model: str,
    effort: str,
    workspace: str | None = None,
) -> refs.SessionSpec:
    effective_model = str(context.pytestconfig.getoption(MODEL_OPTION) or model)
    effective_effort = str(context.pytestconfig.getoption(EFFORT_OPTION) or effort)
    return refs.SessionSpec(harness, effective_model, effective_effort, workspace)


@given(parsers.parse('session configuration "{name}" uses {harness} with model {model} and {effort} effort'))
def configure_session(
    session_config_context: session_contexts.SessionConfigContext,
    name: str,
    harness: str,
    model: str,
    effort: str,
) -> None:
    """Define one session configuration."""
    session_config_context.session_specs.bind(
        name,
        _configured_spec(session_config_context, harness, model, effort),
    )


@given(
    parsers.parse(
        'session configuration "{name}" uses {harness} with model {model} and {effort} effort in a versioned workspace',
    ),
)
def configure_session_in_versioned_workspace(
    versioned_session_config_context: session_contexts.WorkspaceSessionConfigContext,
    name: str,
    harness: str,
    model: str,
    effort: str,
) -> None:
    """Define one session configuration in a versioned workspace."""
    session_context = versioned_session_config_context
    spec = _configured_spec(session_context.common, harness, model, effort, session_context.workspace)
    session_context.common.session_specs.bind(name, spec)


@given(
    parsers.parse(
        'session configuration "{name}" uses {harness} with model {model} and '
        "{effort} effort in the isolated repository workspace",
    ),
)
def configure_session_in_repository_workspace(
    repository_session_config_context: session_contexts.RepositorySessionConfigContext,
    name: str,
    harness: str,
    model: str,
    effort: str,
) -> None:
    """Define one session configuration in the repository workspace."""
    session_context = repository_session_config_context
    session_context.common.session_specs.bind(
        name,
        _configured_spec(
            session_context.common,
            harness,
            model,
            effort,
            session_context.repository.working_directory,
        ),
    )


@given(
    parsers.parse(
        'session configuration "{name}" uses {harness} with model {model} and '
        "{effort} effort in the isolated repository root",
    ),
)
def configure_session_in_repository_root(
    repository_session_config_context: session_contexts.RepositorySessionConfigContext,
    name: str,
    harness: str,
    model: str,
    effort: str,
) -> None:
    """Define one session configuration in the repository root."""
    session_context = repository_session_config_context
    session_context.common.session_specs.bind(
        name,
        _configured_spec(
            session_context.common,
            harness,
            model,
            effort,
            session_context.repository.repository_root,
        ),
    )
