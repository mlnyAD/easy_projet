

from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from django.db import transaction

from apps.documents.models import SignatureRequestDocument
from apps.documents.storage import DocumentStorage


class SignatureArtifactService:
    """
    Gère les fichiers immuables liés à une demande de signature.

    Les fichiers préparés et signés sont stockés séparément des
    DocumentVersion : ils ne deviennent jamais des versions de travail
    du document source.
    """

    PDF_MIME_TYPE = "application/pdf"

    def __init__(
        self,
        *,
        storage: DocumentStorage,
    ) -> None:
        self.storage = storage

    def prepare_pdf(
        self,
        *,
        request_document: SignatureRequestDocument,
    ) -> SignatureRequestDocument:
        """
        Copie la version source PDF vers l'artefact immuable à signer.

        La V1 accepte les documents déjà au format PDF. La conversion
        Office / image vers PDF sera ajoutée ultérieurement comme une
        étape de préparation distincte.
        """

        storage_key: str | None = None

        try:
            with transaction.atomic():
                locked_request_document = (
                    SignatureRequestDocument.objects
                    .select_for_update()
                    .select_related(
                        "signature_request",
                        "source_version",
                    )
                    .get(pk=request_document.pk)
                )

                if locked_request_document.has_prepared_pdf:
                    return locked_request_document

                source_version = (
                    locked_request_document.source_version
                )

                if not self._is_pdf(
                    mime_type=source_version.mime_type,
                    filename=source_version.original_filename,
                ):
                    raise ValueError(
                        "Seuls les documents PDF peuvent être envoyés "
                        "en signature pour le moment."
                    )

                if not self.storage.exists(
                    source_version.storage_key
                ):
                    raise ValueError(
                        "Le fichier source à signer est introuvable."
                    )

                with self.storage.open(
                    source_version.storage_key
                ) as source_content:
                    content_bytes = self._read_content(
                        source_content
                    )

                self._validate_pdf_content(content_bytes)

                storage_key = self._build_storage_key(
                    request_document=locked_request_document,
                    artifact_kind="prepared",
                )

                self.storage.save(
                    storage_key,
                    BytesIO(content_bytes),
                )

                locked_request_document.prepared_storage_key = (
                    storage_key
                )
                locked_request_document.prepared_filename = (
                    self._build_pdf_filename(
                        source_version.original_filename
                    )
                )
                locked_request_document.prepared_mime_type = (
                    self.PDF_MIME_TYPE
                )
                locked_request_document.prepared_file_size = len(
                    content_bytes
                )
                locked_request_document.prepared_checksum = (
                    hashlib.sha256(content_bytes).hexdigest()
                )

                locked_request_document.full_clean()

                locked_request_document.save(
                    update_fields=[
                        "prepared_storage_key",
                        "prepared_filename",
                        "prepared_mime_type",
                        "prepared_file_size",
                        "prepared_checksum",
                        "prepared_at",
                        "updated_at",
                    ]
                )

                return locked_request_document

        except Exception:
            self._delete_if_exists(storage_key)
            raise

    def store_signed_pdf(
        self,
        *,
        request_document: SignatureRequestDocument,
        content: BinaryIO,
        filename: str,
    ) -> SignatureRequestDocument:
        """
        Enregistre le PDF signé retourné par le prestataire.

        Ce fichier est distinct du PDF préparé : il constitue la preuve
        documentaire renvoyée par le service de signature.
        """

        storage_key: str | None = None

        try:
            with transaction.atomic():
                locked_request_document = (
                    SignatureRequestDocument.objects
                    .select_for_update()
                    .select_related("signature_request")
                    .get(pk=request_document.pk)
                )

                if locked_request_document.has_signed_pdf:
                    return locked_request_document

                content_bytes = self._read_content(content)

                self._validate_pdf_content(content_bytes)

                storage_key = self._build_storage_key(
                    request_document=locked_request_document,
                    artifact_kind="signed",
                )

                self.storage.save(
                    storage_key,
                    BytesIO(content_bytes),
                )

                locked_request_document.signed_storage_key = (
                    storage_key
                )
                locked_request_document.signed_filename = (
                    self._normalize_pdf_filename(filename)
                )
                locked_request_document.signed_mime_type = (
                    self.PDF_MIME_TYPE
                )
                locked_request_document.signed_file_size = len(
                    content_bytes
                )
                locked_request_document.signed_checksum = (
                    hashlib.sha256(content_bytes).hexdigest()
                )

                locked_request_document.full_clean()

                locked_request_document.save(
                    update_fields=[
                        "signed_storage_key",
                        "signed_filename",
                        "signed_mime_type",
                        "signed_file_size",
                        "signed_checksum",
                        "signed_at",
                        "updated_at",
                    ]
                )

                return locked_request_document

        except Exception:
            self._delete_if_exists(storage_key)
            raise

    def open_prepared_pdf(
        self,
        *,
        request_document: SignatureRequestDocument,
    ) -> BinaryIO:
        """Ouvre le PDF immuable transmis au prestataire."""

        if not request_document.has_prepared_pdf:
            raise ValueError(
                "Le document de signature ne possède pas de PDF préparé."
            )

        if not self.storage.exists(
            request_document.prepared_storage_key
        ):
            raise ValueError(
                "Le PDF préparé pour la signature est introuvable."
            )

        return self.storage.open(
            request_document.prepared_storage_key
        )

    def open_signed_pdf(
        self,
        *,
        request_document: SignatureRequestDocument,
    ) -> BinaryIO:
        """Ouvre le PDF signé retourné par le prestataire."""

        if not request_document.has_signed_pdf:
            raise ValueError(
                "Le document de signature ne possède pas encore "
                "de PDF signé."
            )

        if not self.storage.exists(
            request_document.signed_storage_key
        ):
            raise ValueError(
                "Le PDF signé est introuvable."
            )

        return self.storage.open(
            request_document.signed_storage_key
        )

    @staticmethod
    def _is_pdf(
        *,
        mime_type: str,
        filename: str,
    ) -> bool:
        return (
            mime_type.strip().lower()
            == SignatureArtifactService.PDF_MIME_TYPE
            or Path(filename).suffix.lower() == ".pdf"
        )

    @staticmethod
    def _read_content(
        content: BinaryIO,
    ) -> bytes:
        data = content.read()

        if not isinstance(data, bytes):
            raise TypeError(
                "Le contenu de signature doit être binaire."
            )

        if not data:
            raise ValueError(
                "Le contenu de signature ne peut pas être vide."
            )

        return data

    @staticmethod
    def _validate_pdf_content(
        content: bytes,
    ) -> None:
        if not content.startswith(b"%PDF-"):
            raise ValueError(
                "Le fichier transmis pour signature doit être un PDF."
            )

    @staticmethod
    def _build_pdf_filename(
        filename: str,
    ) -> str:
        normalized_name = Path(filename.strip()).name
        stem = Path(normalized_name).stem.strip()

        if not stem:
            stem = "document"

        return f"{stem}.pdf"

    @classmethod
    def _normalize_pdf_filename(
        cls,
        filename: str,
    ) -> str:
        normalized_name = Path(filename.strip()).name

        if not normalized_name:
            raise ValueError(
                "Le nom du PDF signé ne peut pas être vide."
            )

        if Path(normalized_name).suffix.lower() != ".pdf":
            return cls._build_pdf_filename(normalized_name)

        return normalized_name

    @staticmethod
    def _build_storage_key(
        *,
        request_document: SignatureRequestDocument,
        artifact_kind: str,
    ) -> str:
        return (
            f"projects/{request_document.signature_request.project_id}/"
            f"signature-requests/"
            f"{request_document.signature_request_id}/"
            f"documents/{request_document.pk}/"
            f"{artifact_kind}/{uuid4().hex}.pdf"
        )

    def _delete_if_exists(
        self,
        storage_key: str | None,
    ) -> None:
        if storage_key is None:
            return

        try:
            if self.storage.exists(storage_key):
                self.storage.delete(storage_key)
        except Exception:
            # L'erreur initiale reste l'information utile à remonter.
            pass