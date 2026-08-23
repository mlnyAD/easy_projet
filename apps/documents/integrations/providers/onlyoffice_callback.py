

from __future__ import annotations

from typing import Any

from apps.documents.integrations.providers.onlyoffice_download import (
    OnlyOfficeDownloadService,
)
from apps.documents.models import DocumentVersion
from apps.documents.services import DocumentVersionService
from apps.documents.storage import (
    DocumentStorage,
    get_document_storage,
)
from apps.users.models import User


class OnlyOfficeCallbackError(RuntimeError):
    """
    Erreur fonctionnelle lors du traitement
    d'un callback ONLYOFFICE.
    """


class OnlyOfficeCallbackService:
    """
    Traite les événements reçus d'ONLYOFFICE.

    La création d'une nouvelle version reste déléguée
    à DocumentVersionService.
    """

    STATUS_EDITING = 1
    STATUS_READY_FOR_SAVE = 2
    STATUS_SAVE_ERROR = 3
    STATUS_CLOSED_WITHOUT_CHANGES = 4
    STATUS_FORCE_SAVE = 6
    STATUS_FORCE_SAVE_ERROR = 7

    def __init__(
        self,
        *,
        storage: DocumentStorage | None = None,
    ) -> None:
        self.storage = (
            storage
            or get_document_storage()
        )

        self.version_service = DocumentVersionService(
            storage=self.storage
        )

    def process(
        self,
        *,
        version: DocumentVersion,
        payload: dict[str, Any],
    ) -> DocumentVersion | None:
        """
        Traite un callback ONLYOFFICE.

        Retourne la nouvelle version lorsqu'une sauvegarde
        a effectivement été enregistrée.
        """

        status = payload.get("status")

        if status != self.STATUS_READY_FOR_SAVE:
            return None

        download_url = payload.get("url")

        if not isinstance(download_url, str):
            raise OnlyOfficeCallbackError(
                "URL du document modifié absente du callback."
            )

        download_url = download_url.strip()

        if not download_url:
            raise OnlyOfficeCallbackError(
                "URL du document modifié absente du callback."
            )

        user = self._resolve_user(
            payload
        )

        content = OnlyOfficeDownloadService.download(
            download_url
        )

        return self.version_service.create_version(
            document=version.document,
            content=content,
            original_filename=version.original_filename,
            mime_type=version.mime_type,
            user=user,
        )

    @staticmethod
    def _resolve_user(
        payload: dict[str, Any],
    ) -> User:
        users = payload.get("users")

        if (
            not isinstance(users, list)
            or not users
        ):
            raise OnlyOfficeCallbackError(
                "Utilisateur ONLYOFFICE absent du callback."
            )

        user_id = str(users[-1]).strip()

        if not user_id:
            raise OnlyOfficeCallbackError(
                "Utilisateur ONLYOFFICE invalide."
            )

        try:
            return User.objects.get(
                pk=user_id
            )
        except (
            User.DoesNotExist,
            ValueError,
            TypeError,
        ) as exc:
            raise OnlyOfficeCallbackError(
                "Utilisateur Easy Projet introuvable."
            ) from exc