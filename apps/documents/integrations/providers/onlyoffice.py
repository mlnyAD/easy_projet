
        
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.urls import reverse

from apps.documents.models import DocumentVersion
from apps.documents.services import DocumentAccessTokenService

from ..base import DocumentIntegration
from ..capabilities import DocumentCapability
from .onlyoffice_jwt import OnlyOfficeJwtService


class OnlyOfficeAdapter(DocumentIntegration):
    """
    Adaptateur ONLYOFFICE Docs.

    Prépare la configuration complète permettant
    l'ouverture d'une DocumentVersion dans ONLYOFFICE.

    Easy Projet reste propriétaire du fichier physique.
    """

    provider_code = "ONLYOFFICE"

    capabilities = frozenset(
        {
            DocumentCapability.OFFICE_EDIT,
            DocumentCapability.OFFICE_VIEW,
        }
    )

    MIME_DOCX = (
        "application/vnd.openxmlformats-officedocument."
        "wordprocessingml.document"
    )

    MIME_XLSX = (
        "application/vnd.openxmlformats-officedocument."
        "spreadsheetml.sheet"
    )

    MIME_PPTX = (
        "application/vnd.openxmlformats-officedocument."
        "presentationml.presentation"
    )

    SUPPORTED_MIME_TYPES = frozenset(
        {
            MIME_DOCX,
            MIME_XLSX,
            MIME_PPTX,
        }
    )

    DOCUMENT_TYPES = {
        ".docx": "word",
        ".xlsx": "cell",
        ".pptx": "slide",
    }

    def supports(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
    ) -> bool:
        return (
            self.provides(capability)
            and version.mime_type
            in self.SUPPORTED_MIME_TYPES
        )

    def open(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        user,
    ) -> dict[str, object]:
        """
        Construit la configuration DocsAPI.DocEditor.

        La configuration retournée contient :
        - l'URL du serveur ONLYOFFICE ;
        - l'URL sécurisée du fichier Easy Projet ;
        - le callback Easy Projet ;
        - l'utilisateur ;
        - le mode lecture/édition ;
        - le JWT signé.
        """

        if not self.supports(
            version=version,
            capability=capability,
        ):
            raise ValueError(
                "Cette version documentaire n'est pas "
                "compatible avec ONLYOFFICE."
            )

        server_url = self._get_server_url()
        easy_projet_url = self._get_easy_projet_url()

        file_type = self._get_file_type(
            version.original_filename
        )

        document_type = self._get_document_type(
            file_type
        )

        content_token = (
            DocumentAccessTokenService.create_token(
                version=version,
            )
        )

        content_path = reverse(
            "documents:version-content",
            kwargs={
                "version_id": version.pk,
            },
        )

        callback_path = reverse(
            "documents:version-callback",
            kwargs={
                "version_id": version.pk,
            },
        )

        content_url = (
            f"{easy_projet_url}"
            f"{content_path}"
            f"?token={content_token}"
        )

        callback_url = (
            f"{easy_projet_url}"
            f"{callback_path}"
        )
        
        print(
            "ONLYOFFICE content_url =",
            content_url,
        )

        print(
            "ONLYOFFICE callback_url =",
            callback_url,
        )

        mode = (
            "edit"
            if capability
            == DocumentCapability.OFFICE_EDIT
            else "view"
        )

        config = {
            "documentType": document_type,

            "document": {
                "fileType": file_type,
                "key": str(version.pk),
                "title": version.original_filename,
                "url": content_url,
            },

            "editorConfig": {
                "callbackUrl": callback_url,
                "mode": mode,

                "user": {
                    "id": str(user.pk),
                    "name": str(user),
                },

                "lang": "fr",
            },
        }

        token = OnlyOfficeJwtService.encode(
            config
        )

        config["token"] = token

        return {
            "provider": self.provider_code,

            "server_url": server_url,

            "api_url": (
                f"{server_url}"
                "/web-apps/apps/api/documents/api.js"
            ),

            "version_id": str(version.pk),

            "document_id": str(
                version.document_id
            ),

            "filename": (
                version.original_filename
            ),

            "mime_type": version.mime_type,

            "capability": capability,

            "config": config,
        }

    @staticmethod
    def _get_server_url() -> str:
        """
        URL du serveur ONLYOFFICE.
        """

        server_url = (
            settings.ONLYOFFICE_URL
            .strip()
            .rstrip("/")
        )

        if not server_url:
            raise RuntimeError(
                "ONLYOFFICE_URL n'est pas configurée."
            )

        return server_url

    @staticmethod
    def _get_easy_projet_url() -> str:
        """
        URL publique d'Easy Projet accessible
        depuis ONLYOFFICE.
        """

        easy_projet_url = (
            settings.EASY_PROJET_PUBLIC_URL
            .strip()
            .rstrip("/")
        )

        if not easy_projet_url:
            raise RuntimeError(
                "EASY_PROJET_PUBLIC_URL "
                "n'est pas configurée."
            )

        return easy_projet_url

    @staticmethod
    def _get_file_type(
        filename: str,
    ) -> str:
        """
        Retourne l'extension attendue par ONLYOFFICE,
        sans le point.
        """

        extension = (
            Path(filename)
            .suffix
            .lower()
        )

        if extension not in (
            OnlyOfficeAdapter.DOCUMENT_TYPES
        ):
            raise ValueError(
                "Format de fichier non pris en charge "
                "par ONLYOFFICE."
            )

        return extension.removeprefix(".")

    @staticmethod
    def _get_document_type(
        file_type: str,
    ) -> str:
        """
        Retourne le type d'éditeur ONLYOFFICE.

        docx -> word
        xlsx -> cell
        pptx -> slide
        """

        extension = (
            f".{file_type.lower()}"
        )

        try:
            return (
                OnlyOfficeAdapter
                .DOCUMENT_TYPES[
                    extension
                ]
            )
        except KeyError as exc:
            raise ValueError(
                "Type de document ONLYOFFICE "
                "non supporté."
            ) from exc        