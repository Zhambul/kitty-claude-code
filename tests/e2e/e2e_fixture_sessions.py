# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide e2e fixture sessions."""

from __future__ import annotations

from tests.e2e import e2e_fixture_dependencies as fixture_dependencies


@fixture_dependencies.application.pytest.fixture
def worktree_changes() -> fixture_dependencies.drivers.refs.WorktreeChanges:
    """Create the named references for worktree changes.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("worktree change")


@fixture_dependencies.application.pytest.fixture
def staged_attachments() -> fixture_dependencies.drivers.refs.StagedAttachments:
    """Create the named references for staged attachments.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("staged attachment")


@fixture_dependencies.application.pytest.fixture
def attachment_bundles() -> fixture_dependencies.drivers.refs.AttachmentBundles:
    """Create the named references for attachment bundles.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("attachment bundle")


@fixture_dependencies.application.pytest.fixture
def controls() -> fixture_dependencies.drivers.refs.Controls:
    """Create the named references for controls.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("control")


@fixture_dependencies.application.pytest.fixture
def skills() -> fixture_dependencies.drivers.refs.Skills:
    """Create the named references for skills.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("skill")


@fixture_dependencies.application.pytest.fixture
def questions() -> fixture_dependencies.drivers.refs.Questions:
    """Create the named references for questions.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("question")


@fixture_dependencies.application.pytest.fixture
def plans() -> fixture_dependencies.drivers.refs.Plans:
    """Create the named references for plans.

    Returns:
        An empty reference collection for one test.

    """
    return fixture_dependencies.drivers.refs.References("plan")
