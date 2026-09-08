# Copyright (c) 2026 Zhambyl Yermagambet
"""Own dashboard models."""

from collections.abc import Mapping
from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict

from harness.runtime import HarnessRuntimeConfigs


class HealthProcess(BaseModel):
    """Represent health process."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    process_id: int


@dataclass(frozen=True)
class _HarnessFlag:
    name: str
    setting: str


@dataclass(frozen=True)
class _DashboardOptions:
    variables: Mapping[str, str]
    log_path: str | None
    harness_runtime_configs: HarnessRuntimeConfigs
    harness_flags: tuple[_HarnessFlag, ...]


@dataclass
class _ParsedOptions:
    variables: dict[str, str]
    log_path: str | None
    harness_flags: list[_HarnessFlag]
