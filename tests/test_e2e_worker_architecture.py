# Copyright (c) 2026 Zhambyl Yermagambet
"""Verify E2E feature language stays harness-neutral."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from tests import e2e_feature_scenarios as feature_scenarios

if TYPE_CHECKING:
    from pathlib import Path


def worker_scenario_violations(
    path: Path,
    scenario: feature_scenarios.FeatureScenario,
) -> tuple[str, ...]:
    """Return invalid worker-selection rules for one scenario.

    Returns:
        Invalid worker-selection rules for one scenario.

    """
    if "<worker>" not in scenario.behavior:
        return ()
    location = f"{path.relative_to(feature_scenarios.ROOT)}: {scenario.title}"
    violations: list[str] = []
    if scenario.kind != "Scenario Outline":
        violations.append(f"{location} uses a worker value without a Scenario Outline")
    if not re.search(r"^\s*\|.*\bworker\b.*\|", scenario.body, re.MULTILINE):
        violations.append(f"{location} has no worker examples column")
    return tuple(violations)


def test_worker_behavior_is_selected_per_work() -> None:
    """Verify worker behavior is selected per work or by examples rows."""
    violations = worker_violations()
    assert not violations


def worker_violations() -> list[str]:
    """Return worker-selection violations from every feature file.

    Returns:
        Worker-selection violations from every feature file.

    """
    violations: list[str] = []
    for path in sorted(feature_scenarios.FEATURES.glob("*.feature")):
        for scenario in feature_scenarios.scenarios(path):
            violations.extend(worker_scenario_violations(path, scenario))
    return violations


def test_e2e_does_not_use_legacy_codex_subagent() -> None:
    """Verify end-to-end tests do not use legacy Codex subagent tools."""
    e2e_root = feature_scenarios.ROOT / "tests" / "e2e"
    violations = [
        str(path.relative_to(feature_scenarios.ROOT))
        for path in sorted(e2e_root.rglob("*"))
        if path.suffix in {".feature", ".py"}
        and "multi_agent_v1__" in path.read_text(encoding=feature_scenarios.TEXT_ENCODING)
    ]
    assert not violations


def test_feature_language_does_not_name_native() -> None:
    """Verify feature language does not name native harness tools."""
    native_tools = re.compile(r"multi_agent_v\d+__|\bAgent tool\b|\bSkill tool\b|\$[a-z][a-z0-9-]+")
    violations = [
        str(path.relative_to(feature_scenarios.ROOT))
        for path in sorted(feature_scenarios.FEATURES.glob("*.feature"))
        if native_tools.search(path.read_text(encoding=feature_scenarios.TEXT_ENCODING))
    ]
    assert not violations
