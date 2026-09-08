# Copyright (c) 2026 Zhambyl Yermagambet
"""Resolve one singleton dependency graph for each application.

Provider signatures declare the graph for FastAPI and background services.
The application owns the instance registry, so tests and applications do not
share service objects.
"""

import functools
import inspect
from collections.abc import Callable, Mapping
from typing import (
    Any,
    Concatenate,
    Protocol,
    cast,
    get_type_hints,
)

from fastapi import Request

from app.injection_types import TypeHint, provider_from_hint

Instances = dict[Any, Any]


class SingletonProvider[**ProviderArguments, Instance](Protocol):
    """Callable provider with its original build function."""

    __signature__: inspect.Signature
    build: Callable[ProviderArguments, Instance]

    def __call__(
        self,
        request: Request,
        *args: ProviderArguments.args,
        **keywords: ProviderArguments.kwargs,
    ) -> Instance:
        """Build or return one scoped instance."""
        ...


def registry() -> Instances:
    """Return a fresh singleton scope.

    Returns:
        A fresh singleton scope.

    """
    instances: Instances = {}
    return instances


def seed[Instance](
    instances: Instances,
    provider: Callable[..., Instance],
    instance: Instance,
) -> None:
    """Set one startup value before graph resolution."""
    build = getattr(provider, "build", provider)
    instances[build] = instance


def singleton[**ProviderArguments, Instance](
    build: Callable[ProviderArguments, Instance],
) -> Callable[Concatenate[Request, ProviderArguments], Instance]:
    """Return a provider that builds one instance per application.

    Returns:
        A provider that builds one instance per application.

    """
    signature = inspect.signature(build)
    provider_parameters = (
        inspect.Parameter(
            "request",
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            annotation=Request,
        ),
        *signature.parameters.values(),
    )
    provider = cast(
        "SingletonProvider[ProviderArguments, Instance]",
        functools.partial(_provide_singleton, build),
    )
    functools.update_wrapper(provider, build)
    provider.__signature__ = signature.replace(parameters=provider_parameters)
    provider.build = build
    return cast(
        "Callable[Concatenate[Request, ProviderArguments], Instance]",
        provider,
    )


def resolve[Instance](
    instances: Instances,
    provider: Callable[..., Instance],
) -> Instance:
    """Build one provider outside a request from the declared graph.

    Returns:
        The instance.

    """
    build = getattr(provider, "build", provider)
    existing_instance = instances.get(build)
    if existing_instance is not None:
        return cast("Instance", existing_instance)
    hints = get_type_hints(build, include_extras=True)
    dependencies = _dependencies(instances, build, hints)
    built_instance: Instance = build(**dependencies)
    instances[build] = built_instance
    return built_instance


def _provide_singleton[**ProviderArguments, Instance](
    singleton_build: Callable[ProviderArguments, Instance],
    request: Request,
    *args: ProviderArguments.args,
    **dependencies: ProviderArguments.kwargs,
) -> Instance:
    instances: Instances = request.app.state.instances
    if singleton_build not in instances:
        instances[singleton_build] = singleton_build(*args, **dependencies)
    instance: Instance = instances[singleton_build]
    return instance


def _dependencies(
    instances: Instances,
    build: Callable[..., Any],
    hints: Mapping[str, TypeHint],
) -> Instances:
    dependencies: Instances = {}
    for name in inspect.signature(build).parameters:
        dependency_provider = provider_from_hint(name, hints.get(name))
        dependencies[name] = resolve(instances, dependency_provider)
    return dependencies
