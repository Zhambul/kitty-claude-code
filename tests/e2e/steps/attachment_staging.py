# Copyright (c) 2026 Zhambyl Yermagambet
"""Steps that stage and check launch attachments."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pytest_bdd import parsers, then, when

from tests.e2e.testkit.attachments import attachment_reference, marker_png
from tests.e2e.testkit.references import AttachmentBundleRef

if TYPE_CHECKING:
    from sdk.client import BaqylauClient
    from tests.e2e.testkit.references import AttachmentBundles, StagedAttachments


@when(parsers.parse("I stage text attachment '{file_name}' with content '{file_content}' as \"{attachment_name}\""))
def stage_text_attachment(
    client: BaqylauClient,
    staged_attachments: StagedAttachments,
    file_name: str,
    file_content: str,
    attachment_name: str,
) -> None:
    """Stage one text attachment."""
    staged_attachments.bind(
        attachment_name,
        client.uploads.stage(name=file_name, media_type="text/plain", file_content=file_content.encode()),
    )


@when(parsers.parse("I stage marker image '{file_name}' showing '{marker}' as \"{attachment_name}\""))
def stage_marker_image(
    client: BaqylauClient,
    staged_attachments: StagedAttachments,
    file_name: str,
    marker: str,
    attachment_name: str,
) -> None:
    """Stage one marker image."""
    staged_attachments.bind(
        attachment_name,
        client.uploads.stage(name=file_name, media_type="image/png", file_content=marker_png(marker)),
    )


@when(parsers.parse('I group staged attachments as "{bundle_name}"'))
def group_staged_attachments(
    staged_attachments: StagedAttachments,
    attachment_bundles: AttachmentBundles,
    bundle_name: str,
    datatable: list[list[str]],
) -> None:
    """Group named staged attachments into one bundle.

    Raises:
        AssertionError: If the data table has an invalid attachment layout.

    """
    if not datatable or datatable[0] != ["attachment"]:
        message = "attachment bundle table must have an attachment column"
        raise AssertionError(message)
    names = attachment_names(datatable[1:])
    attachments = tuple(attachment_reference(staged_attachments.get(name)) for name in names)
    attachment_bundles.bind(bundle_name, AttachmentBundleRef(attachments))


def attachment_names(rows: list[list[str]]) -> tuple[str, ...]:
    """Return one non-empty attachment name for each table row.

    Returns:
        The attachment names.

    Raises:
        AssertionError: If a row is malformed or the list is empty.

    """
    names: list[str] = []
    for row in rows:
        if len(row) != 1:
            message = "attachment bundle table rows must have one attachment"
            raise AssertionError(message)
        name = row[0].strip()
        if not name:
            message = "attachment bundle names must not be empty"
            raise AssertionError(message)
        names.append(name)
    if not names:
        message = "attachment bundle names must not be empty"
        raise AssertionError(message)
    return tuple(names)


@then(parsers.parse("staged attachment \"{name}\" is text file '{file_name}'"))
def staged_attachment_is_text_file(staged_attachments: StagedAttachments, name: str, file_name: str) -> None:
    """Verify one staged text attachment."""
    staged = staged_attachments.get(name)
    assert staged.ok
    assert (staged.name, staged.mime, staged.is_image) == (file_name, "text/plain", False)


@then(parsers.parse("staged attachment \"{name}\" is PNG image '{file_name}'"))
def staged_attachment_is_png_image(staged_attachments: StagedAttachments, name: str, file_name: str) -> None:
    """Verify one staged PNG attachment."""
    staged = staged_attachments.get(name)
    assert staged.ok
    assert (staged.name, staged.mime, staged.is_image) == (file_name, "image/png", True)
