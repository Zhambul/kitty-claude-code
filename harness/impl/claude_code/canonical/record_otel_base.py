# Copyright (c) 2026 Zhambyl Yermagambet
"""Record otel base."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from harness.impl.claude_code.canonical.record_common import OPEN_FOREIGN


class OTelAttributeValue(BaseModel):
    """Represent otel attribute value."""

    model_config = OPEN_FOREIGN
    string_value: Annotated[str | None, Field(alias="stringValue")] = None
    int_value: Annotated[str | int | None, Field(alias="intValue")] = None
    double_value: Annotated[int | float | None, Field(alias="doubleValue")] = None

    def scalar(self) -> str | int | float | None:
        """Return the scalar.

        Returns:
            Scalar.

        """
        return self.string_value or self.int_value or self.double_value


class OTelAttribute(BaseModel):
    """Represent otel attribute."""

    model_config = OPEN_FOREIGN
    key: str = ""
    attribute_value: OTelAttributeValue = Field(default_factory=OTelAttributeValue, alias="value")


class OTelDataPoint(BaseModel):
    """Represent otel data point."""

    model_config = OPEN_FOREIGN
    attributes: list[OTelAttribute] = Field(default_factory=list)
    as_double: Annotated[int | float | None, Field(alias="asDouble")] = None
    as_int: Annotated[str | int | None, Field(alias="asInt")] = None

    def amount(self) -> str | int | float | None:
        """Return the numeric amount.

        Returns:
            The numeric amount.

        """
        return self.as_int if self.as_double is None else self.as_double

    def attribute(self, key: str) -> str | int | float | None:
        """Return the attribute.

        Returns:
            Attribute.

        """
        return next(
            (attribute.attribute_value.scalar() for attribute in self.attributes if attribute.key == key),
            None,
        )


class OTelSum(BaseModel):
    """Represent otel sum."""

    model_config = OPEN_FOREIGN
    data_points: Annotated[list[OTelDataPoint], Field(alias="dataPoints")] = Field(default_factory=list)


class OTelMetric(BaseModel):
    """Represent otel metric."""

    model_config = OPEN_FOREIGN
    name: str = ""
    sum: OTelSum | None = None

    def usage_points(self) -> tuple[OTelDataPoint, ...]:
        """Return data points for a usage metric.

        Returns:
            The usage data points.

        """
        is_usage = "token.usage" in self.name or "cost.usage" in self.name
        if is_usage and self.sum is not None:
            return tuple(self.sum.data_points)
        return ()


class OTelScopeMetrics(BaseModel):
    """Represent otel scope metrics."""

    model_config = OPEN_FOREIGN
    metrics: list[OTelMetric] = Field(default_factory=list)


class OTelResourceMetrics(BaseModel):
    """Represent otel resource metrics."""

    model_config = OPEN_FOREIGN
    scope_metrics: Annotated[list[OTelScopeMetrics], Field(alias="scopeMetrics")] = Field(default_factory=list)
