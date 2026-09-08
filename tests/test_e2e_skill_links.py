# Copyright (c) 2026 Zhambyl Yermagambet
"""Check ownership of existing test skill links."""

from pathlib import Path

import pytest

from tests.e2e.testkit.skill_fixtures import SKILL_FIXTURE_ROOT, SkillFixtures

SKILL_NAME = "baqylau-e2e-communication"


def test_existing_skill_link_is_not_removed(tmp_path: Path) -> None:
    """Reuse a matching link without taking ownership of it."""
    source = (SKILL_FIXTURE_ROOT / SKILL_NAME).resolve()
    link = tmp_path / ".agents/skills" / SKILL_NAME
    link.parent.mkdir(parents=True)
    link.symlink_to(source, target_is_directory=True)
    fixtures = SkillFixtures(str(tmp_path))
    available = fixtures.make_available("codex", SKILL_NAME)
    assert (available.source, available.installed) == (source, link)
    assert fixtures.make_available("codex", SKILL_NAME) is available
    fixtures.close()
    assert link.is_symlink() and link.resolve() == source


def test_existing_skill_file_is_not_replaced(tmp_path: Path) -> None:
    """Reject a conflicting file and leave its content unchanged."""
    link = tmp_path / ".agents/skills" / SKILL_NAME
    link.parent.mkdir(parents=True)
    link.write_text("keep", encoding="utf-8")
    fixtures = SkillFixtures(str(tmp_path))
    with pytest.raises(AssertionError, match="test skill destination already exists"):
        fixtures.make_available("codex", SKILL_NAME)
    fixtures.close()
    assert link.read_text(encoding="utf-8") == "keep"
