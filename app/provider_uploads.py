# Copyright (c) 2026 Zhambyl Yermagambet
"""Provide staged-upload services."""

from typing import Annotated

from fastapi import Depends

from app import provider_audit_storage as audit_providers, provider_auxiliary_storage as storage_providers
from app.injection import singleton
from app.services import uploads as upload_service


@singleton
def uploads(
    storage: storage_providers.UploadStorage,
    audit: audit_providers.Recorder,
) -> upload_service.UploadService:
    """Return the staged-upload service.

    Returns:
        Staged-upload service.

    """
    return upload_service.UploadService(storage, audit)


Uploads = Annotated[upload_service.UploadService, Depends(uploads)]
