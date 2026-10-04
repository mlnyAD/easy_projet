

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO

from apps.documents.models import (
    DocumentVersion,
    SignatureRequest,
)
from apps.integrations.models import ExternalIntegration

from .base import DocumentIntegration
from .capabilities import DocumentCapability


@dataclass(frozen=True, slots=True)
class SignatureDocumentSubmission:
    """
    Représente un PDF immuable transmis au prestataire.
    """

    request_document_id: str
    filename: str
    content: BinaryIO
    checksum: str


@dataclass(frozen=True, slots=True)
class SignatureRecipientSubmission:
    """
    Représente un signataire transmis au prestataire.
    """

    recipient_id: str
    full_name: str
    email: str
    signing_order: int


@dataclass(frozen=True, slots=True)
class SignatureSubmission:
    """
    Résultat de la création et de l'envoi d'une demande externe.
    """

    provider_request_id: str


class SignatureIntegration(DocumentIntegration, ABC):
    """
    Contrat spécifique aux fournisseurs de signature électronique.

    Les adaptateurs Documenso, Yousign ou tout autre fournisseur
    implémenteront ce contrat sans modifier le métier Easy Projet.
    """

    capabilities = frozenset(
        {
            DocumentCapability.SIGN,
        }
    )

    def supports(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
    ) -> bool:
        """
        La V1 transmet exclusivement des PDF au prestataire.
        """

        return (
            self.provides(capability)
            and capability == DocumentCapability.SIGN
            and (
                version.mime_type.lower()
                == "application/pdf"
                or version.original_filename.lower().endswith(
                    ".pdf"
                )
            )
        )

    def open(
        self,
        *,
        version: DocumentVersion,
        capability: DocumentCapability,
        user,
        return_url: str | None = None,
    ):
        """
        Une signature ne correspond pas à une ouverture de document.
        """

        raise NotImplementedError(
            "La signature électronique utilise "
            "create_signature_request()."
        )

    @abstractmethod
    def create_signature_request(
        self,
        *,
        external_integration: ExternalIntegration,
        signature_request: SignatureRequest,
        documents: tuple[SignatureDocumentSubmission, ...],
        recipients: tuple[SignatureRecipientSubmission, ...],
    ) -> SignatureSubmission:
        """
        Crée et distribue la demande chez le fournisseur.

        Les secrets sont obtenus depuis
        ``external_integration.credential_reference``.
        """

        raise NotImplementedError

    @abstractmethod
    def cancel_signature_request(
        self,
        *,
        external_integration: ExternalIntegration,
        signature_request: SignatureRequest,
    ) -> None:
        """Annule une demande encore active chez le fournisseur."""

        raise NotImplementedError

    @abstractmethod
    def verify_webhook(
        self,
        *,
        external_integration: ExternalIntegration,
        headers: dict[str, str],
        body: bytes,
    ) -> bool:
        """Vérifie l'authenticité d'un webhook fournisseur."""

        raise NotImplementedError