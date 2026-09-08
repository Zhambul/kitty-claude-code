# Copyright (c) 2026 Zhambyl Yermagambet
"""Publish the API OpenAPI documents."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import partial
from typing import cast

import yaml
from fastapi import FastAPI, Response
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.models import Components, PathItem
from pydantic import BaseModel, ConfigDict

FrameworkDocument = dict[str, object]


class PublishedOpenAPI(BaseModel):
    """Represent the published FastAPI schema."""

    model_config = ConfigDict(extra="allow")
    paths: Mapping[str, PathItem] | None = None
    components: Components | None = None


def configure(web: FastAPI) -> None:
    """Configure published JSON and YAML OpenAPI documents."""
    generate = web.openapi
    web.openapi = partial(_document, web, generate)  # type: ignore[method-assign]
    web.add_api_route("/openapi.yaml", partial(_yaml, web), methods=["GET"], include_in_schema=False)


def _document(web: FastAPI, generate: Callable[[], FrameworkDocument]) -> FrameworkDocument:
    if web.openapi_schema is None:
        web.openapi_schema = _published(generate())
    return cast("FrameworkDocument", web.openapi_schema)


def _published(framework_document: FrameworkDocument) -> FrameworkDocument:
    schema = PublishedOpenAPI.model_validate(framework_document)
    _remove_validation_responses(schema)
    _remove_validation_schemas(schema)
    return cast("FrameworkDocument", jsonable_encoder(schema, by_alias=True, exclude_none=True))


def _remove_validation_responses(published_open_api: PublishedOpenAPI) -> None:
    if published_open_api.paths is None:
        return
    for raw_path in published_open_api.paths.values():
        for operation in (
            raw_path.get,
            raw_path.put,
            raw_path.post,
            raw_path.delete,
            raw_path.options,
            raw_path.head,
            raw_path.patch,
            raw_path.trace,
        ):
            if operation is not None and operation.responses is not None:
                operation.responses.pop("422", None)


def _remove_validation_schemas(published_open_api: PublishedOpenAPI) -> None:
    if published_open_api.components is not None and published_open_api.components.schemas is not None:
        published_open_api.components.schemas.pop("HTTPValidationError", None)
        published_open_api.components.schemas.pop("ValidationError", None)


def _yaml(web: FastAPI) -> Response:
    document = yaml.safe_dump(web.openapi(), sort_keys=False, allow_unicode=True)
    return Response(document, media_type="application/yaml")
