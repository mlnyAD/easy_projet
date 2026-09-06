

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from django.db import transaction

from apps.documents.models import (
    Document,
    DocumentHistory,
    DocumentVersion,
)
from apps.documents.storage import DocumentStorage
from apps.users.models import User


class DocumentVersionService:
    """
    Service de création des versions physiques d'un document.

    Responsabilités :
    - calculer le numéro de version ;
    - calculer l'empreinte SHA-256 ;
    - déterminer la taille du fichier ;
    - générer une clé de stockage ;
    - enregistrer le contenu physique ;
    - créer DocumentVersion ;
    - mettre à jour Document.current_version ;
    - historiser l'opération.

    Le service ne connaît pas l'origine du contenu :
    import, OnlyOffice, CAD, API, etc.
    """

    def __init__(
        self,
        storage: DocumentStorage,
    ) -> None:
        self.storage = storage

    def create_version(
        self,
        *,
        document: Document,
        content: BinaryIO,
        original_filename: str,
        mime_type: str,
        user: User,
    ) -> DocumentVersion:
        """
        Crée une nouvelle version du document.

        Le numéro de version est déterminé exclusivement
        par le système.
        """

        filename = self._normalize_filename(
            original_filename
        )

        content_bytes = self._read_content(
            content
        )

        checksum = hashlib.sha256(
            content_bytes
        ).hexdigest()

        file_size = len(content_bytes)

        storage_key: str | None = None

        try:
            with transaction.atomic():

                locked_document = (
                    Document.objects
                    .select_for_update()
                    .get(pk=document.pk)
                )

                version_number = (
                    self._get_next_version_number(
                        locked_document
                    )
                )

                storage_key = self._build_storage_key(
                    document=locked_document,
                    version_number=version_number,
                    original_filename=filename,
                )

                self.storage.save(
                    storage_key,
                    BytesIO(content_bytes),
                )

                version = DocumentVersion(
                    document=locked_document,
                    version_number=version_number,
                    original_filename=filename,
                    storage_key=storage_key,
                    mime_type=mime_type.strip(),
                    file_size=file_size,
                    checksum=checksum,
                    created_by=user,
                )

                version.full_clean()
                version.save()

                locked_document.current_version = version

                locked_document.full_clean()

                locked_document.save(
                    update_fields=[
                        "current_version",
                        "updated_at",
                    ]
                )

                history = DocumentHistory(
                    document=locked_document,
                    version=version,
                    action=(
                        DocumentHistory.Action.VERSION_CREATED
                    ),
                    user=user,
                    details=(
                        f"Création de la version "
                        f"{version_number}."
                    ),
                )

                history.full_clean()
                history.save()

                return version

        except Exception:
            if (
                storage_key is not None
                and self.storage.exists(storage_key)
            ):
                self.storage.delete(storage_key)

            raise

    @staticmethod
    def _get_next_version_number(
        document: Document,
    ) -> int:
        """
        Retourne le prochain numéro de version.

        Le Document doit avoir été verrouillé auparavant
        avec select_for_update().
        """

        last_version = (
            document.versions
            .order_by("-version_number")
            .first()
        )

        if last_version is None:
            return 1

        return last_version.version_number + 1

    @staticmethod
    def _read_content(
        content: BinaryIO,
    ) -> bytes:
        """
        Lit le contenu fourni.

        Le stockage définitif sera effectué à partir
        de cette représentation binaire.
        """

        data = content.read()

        if not isinstance(data, bytes):
            raise TypeError(
                "Le contenu documentaire doit être binaire."
            )

        if not data:
            raise ValueError(
                "Le contenu documentaire ne peut pas être vide."
            )

        return data

    @staticmethod
    def _normalize_filename(
        original_filename: str,
    ) -> str:
        """
        Nettoie et valide le nom du fichier d'origine.

        Aucun chemin fourni par le client n'est conservé.
        """

        filename = Path(
            original_filename.strip()
        ).name

        if not filename:
            raise ValueError(
                "Le nom du fichier ne peut pas être vide."
            )

        if filename in {".", ".."}:
            raise ValueError(
                "Nom de fichier invalide."
            )

        return filename

    @staticmethod
    def _build_storage_key(
        *,
        document: Document,
        version_number: int,
        original_filename: str,
    ) -> str:
        """
        Génère une clé physique indépendante
        de l'arborescence documentaire utilisateur.

        Le UUID évite toute dépendance technique
        au nom fonctionnel du fichier.
        """

        extension = Path(
            original_filename
        ).suffix.lower()

        physical_name = (
            f"{uuid4().hex}{extension}"
        )

        return (
            f"projects/{document.project_id}/"
            f"documents/{document.pk}/"
            f"versions/{version_number}/"
            f"{physical_name}"
        )