# Copyright (c) 2026 Zhambyl Yermagambet
"""Own shared Codex control dependencies."""

from domain.ids import HarnessName
from harness.impl.codex.continuity import RewindContinuity
from harness.runtime import default_harness_runtime_configs

rewind_continuity = RewindContinuity()
DEFAULT_RUNTIME_CONFIG = default_harness_runtime_configs().for_harness(HarnessName.CODEX)
