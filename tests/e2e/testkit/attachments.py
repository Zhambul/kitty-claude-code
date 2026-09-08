# Copyright (c) 2026 Zhambyl Yermagambet
"""Typed attachment references and deterministic marker images."""

from __future__ import annotations

import string
from io import BytesIO
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

from api.controls.models.attachment_reference import AttachmentReferenceBody

MARKER_FONT_SIZE = 180
MARKER_PADDING = 48

if TYPE_CHECKING:
    from api.application.models.files.upload_response import UploadResponse


def attachment_reference(upload: UploadResponse) -> AttachmentReferenceBody:
    """Convert an upload response to a control attachment reference.

    Returns:
        The reference with the uploaded path, display name, and media type.

    """
    return AttachmentReferenceBody(
        local_path=upload.path,
        display_name=upload.name,
        media_type=upload.mime,
    )


def _marker_image(
    marker: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    bounds: tuple[float, float, float, float],
) -> Image.Image:
    width = _marker_span(bounds[0], bounds[2])
    height = _marker_span(bounds[1], bounds[3])
    image = Image.new("RGB", (width, height), "white")
    ImageDraw.Draw(image).text(
        (MARKER_PADDING - bounds[0], MARKER_PADDING - bounds[1]),
        marker,
        fill="black",
        font=font,
    )
    return image


def _marker_span(first_edge: float, last_edge: float) -> int:
    """Return one padded marker dimension.

    Returns:
        One padded marker dimension.

    """
    return int(last_edge - first_edge + 2 * MARKER_PADDING)


def _validate_marker(marker: str) -> None:
    if not marker or any(character not in string.digits for character in marker):
        message = "an image marker must contain decimal digits only"
        raise ValueError(message)


def marker_png(marker: str) -> bytes:
    """Create a large RGB PNG that shows only the supplied decimal digits.

    Returns:
        A large RGB PNG that shows only the supplied decimal digits.

    """
    _validate_marker(marker)
    font = ImageFont.load_default(size=MARKER_FONT_SIZE)
    measure = Image.new("RGB", (1, 1), "white")
    bounds = ImageDraw.Draw(measure).textbbox((0, 0), marker, font=font)
    image = _marker_image(marker, font, bounds)
    result = BytesIO()
    image.save(result, format="PNG", optimize=True)
    return result.getvalue()
