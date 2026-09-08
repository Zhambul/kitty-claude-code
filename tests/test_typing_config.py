# Copyright (c) 2026 Zhambyl Yermagambet
"""Tests for static type configuration."""

from __future__ import annotations

import pytest

from tests.typing_config_policy import mypy_exempt_packages, package_needs_type_exemption, ruff_annotation_exemptions

FULL_TYPECHECK_TIMEOUT_SECONDS = 180


def test_ruff_has_no_annotation_exemptions() -> None:
    """Require annotations in every Python file."""
    assert not ruff_annotation_exemptions()


@pytest.mark.timeout(FULL_TYPECHECK_TIMEOUT_SECONDS)
def test_no_type_exemption_outlives_migration() -> None:
    """Require removal of a Mypy exemption after migration."""
    exempt = sorted(mypy_exempt_packages())
    still_needed = [package for package in exempt if package_needs_type_exemption(package)]
    assert exempt == still_needed, "delete Mypy exemptions that no longer protect a package"
