# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that read harness lists and catalogs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, when

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.references import HarnessCatalogs, HarnessLists


@when(parsers.parse('I read the installed harnesses as "{name}"'))
def read_installed_harnesses(client: BaqylauClient, harness_lists: HarnessLists, name: str) -> None:
    """Read and name the installed harness list."""
    harness_lists.bind(name, client.harnesses.list())


@when(parsers.parse('I read the {harness} catalog as "{name}"'))
def read_harness_catalog(
    client: BaqylauClient,
    workspace: str,
    harness_catalogs: HarnessCatalogs,
    harness: str,
    name: str,
) -> None:
    """Read and name one harness catalog."""
    harness_catalogs.bind(name, client.harnesses.catalog(harness, workspace=workspace))
