# Copyright (c) 2026 Zhambyl Yermagambet
"""Declare the Claude usage response fields that Baqylau reads."""

from pydantic import BaseModel, ConfigDict

_FOREIGN = ConfigDict(extra="ignore", frozen=True)


class LiveUsageWindow(BaseModel):
    """Describe an account usage window."""

    model_config = _FOREIGN
    utilization: float | int | None = None
    resets_at: str | None = None


class LiveModelScopedWindow(BaseModel):
    """Describe a model-specific usage window."""

    model_config = _FOREIGN
    display_name: str | None = None
    utilization: float | int | None = None
    resets_at: str | None = None


class LiveLimitModel(BaseModel):
    """Describe the model in a usage limit."""

    model_config = _FOREIGN
    display_name: str


class LiveLimitScope(BaseModel):
    """Describe the scope of a usage limit."""

    model_config = _FOREIGN
    model: LiveLimitModel | None = None


class LiveLimit(BaseModel):
    """Describe one usage limit."""

    model_config = _FOREIGN
    kind: str
    percent: float | int
    resets_at: str | None = None
    scope: LiveLimitScope | None = None


class LiveRateLimits(BaseModel):
    """Describe all live rate limits in the response."""

    model_config = _FOREIGN
    five_hour: LiveUsageWindow | None = None
    seven_day: LiveUsageWindow | None = None
    model_scoped: tuple[LiveModelScopedWindow, ...] | None = None
    limits: tuple[LiveLimit, ...] = ()


class GetUsageResponse(BaseModel):
    """Describe a Claude usage response."""

    model_config = _FOREIGN
    rate_limits: LiveRateLimits | None = None
    rate_limits_available: bool
    subscription_type: str | None = None
