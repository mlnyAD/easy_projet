

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.urls import reverse

from apps.documents.models import DocumentVersion
from apps.documents.services import (
    DocumentAccessTokenService,
)

from ..base import DocumentIntegration
from ..capabilities import DocumentCapability


class CadViewerAdapter(
    DocumentIntegration
):
    """
    Adaptateur CADViewer.

    Easy Projet reste propriétaire du document physique.

    CADViewer reçoit une URL temporaire sécurisée lui
    permettant de récupérer la DocumentVersion à afficher.
    """

    provider_code = "CADVIEWER"

    capabilities = frozenset(
        {
            DocumentCapability.CAD_VIEW,
        }
    )

    SUPPORTED_EXTENSIONS = frozenset(
        {
            ".dwg",
            ".dxf",
            ".dwf",
        }
    )

    def supports(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
    ) -> bool:
        if not self.provides(
            capability
        ):
            return False

        extension = (
            Path(
                version.original_filename
            )
            .suffix
            .lower()
        )

        return (
            extension
            in self.SUPPORTED_EXTENSIONS
        )

    def open(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        user,
    ) -> dict[str, object]:
        """
        Prépare la configuration d'ouverture CADViewer.
        """

        if not self.supports(
            version=version,
            capability=capability,
        ):
            raise ValueError(
                "Cette version documentaire "
                "n'est pas compatible avec CADViewer."
            )

        frontend_url = (
            settings.CADVIEWER_FRONTEND_URL
            .strip()
            .rstrip("/")
        )

        backend_url = (
            settings.CADVIEWER_BACKEND_URL
            .strip()
            .rstrip("/")
        )

        cadviewer_cvkey = (
            settings.CADVIEWER_CVKEY
            .strip()
        )

        easy_projet_public_url = (
            settings.EASY_PROJET_PUBLIC_URL
            .strip()
            .rstrip("/")
        )

        if not frontend_url:
            raise RuntimeError(
                "CADVIEWER_FRONTEND_URL "
                "n'est pas configurée."
            )

        if not backend_url:
            raise RuntimeError(
                "CADVIEWER_BACKEND_URL "
                "n'est pas configurée."
            )

        if not cadviewer_cvkey:
            raise RuntimeError(
                "CADVIEWER_CVKEY "
                "n'est pas configurée."
            )

        if not easy_projet_public_url:
            raise RuntimeError(
                "EASY_PROJET_PUBLIC_URL "
                "n'est pas configurée."
            )

        token = (
            DocumentAccessTokenService
            .create_token(
                version=version,
            )
        )

        content_path = reverse(
            "documents:version-cad-content",
            kwargs={
                "version_id": version.pk,
                "filename": version.original_filename,
            },
        )
        
        content_url = (
            f"{easy_projet_public_url}"
            f"{content_path}"
            f"?token={token}"
        )

        return {
            "provider": self.provider_code,
            "frontend_url": frontend_url,
            "backend_url": backend_url,
            "content_url": content_url,
            "cvkey": cadviewer_cvkey,
            "version_id": str(version.pk),
            "document_id": str(
                version.document_id
            ),
            "filename": (
                version.original_filename
            ),
            "mime_type": version.mime_type,
            "capability": capability,
        }