
            
from __future__ import annotations

from contextlib import ExitStack
from dataclasses import dataclass
from typing import Sequence

from django.db import transaction
from django.utils import timezone

from apps.documents.integrations import (
    DocumentIntegrationRegistry,
    SignatureDocumentSubmission,
    SignatureIntegration,
    SignatureRecipientSubmission,
    registry,
)
from apps.documents.models import (
    DocumentVersion,
    SignatureRequest,
    SignatureRequestDocument,
    SignatureRequestRecipient,
)
from apps.integrations.models import ExternalIntegration
from apps.projects.models import Project
from apps.users.models import User

from .signature_artifact_service import SignatureArtifactService


@dataclass(frozen=True, slots=True)
class SignatureRecipientInput:
    """
    Données d'un signataire avant leur persistance.
    """

    full_name: str
    email: str
    signing_order: int = 1
    user: User | None = None


class SignatureService:
    """
    Service métier des demandes de signature électronique.

    Il gère la création du brouillon, la préparation des PDF immuables
    et l'envoi effectif par l'intégration externe configurée.
    """

    def __init__(
        self,
        *,
        artifact_service: SignatureArtifactService,
        integration_registry: (
            DocumentIntegrationRegistry | None
        ) = None,
    ) -> None:
        self.artifact_service = artifact_service
        self.integration_registry = (
            integration_registry
            or registry
        )

    def create_draft(
        self,
        *,
        project: Project,
        versions: Sequence[DocumentVersion],
        recipients: Sequence[SignatureRecipientInput],
        external_integration: ExternalIntegration,
        title: str,
        user: User,
    ) -> SignatureRequest:
        """
        Crée une demande de signature en brouillon.

        Chaque version est copiée dans un PDF immuable. Toute modification
        ultérieure du document de travail n'altère donc pas le contenu
        envoyé aux signataires.
        """

        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError(
                "Le titre de la demande de signature "
                "ne peut pas être vide."
            )

        normalized_versions = tuple(versions)

        if not normalized_versions:
            raise ValueError(
                "Sélectionnez au moins un document à signer."
            )

        normalized_recipients = self._normalize_recipients(
            recipients
        )

        self._validate_external_integration(
            project=project,
            external_integration=external_integration,
        )

        self._validate_versions(
            project=project,
            versions=normalized_versions,
        )

        stored_artifact_keys: list[str] = []

        try:
            with transaction.atomic():
                signature_request = SignatureRequest(
                    project=project,
                    external_integration=external_integration,
                    title=normalized_title,
                    status=SignatureRequest.Status.DRAFT,
                    created_by=user,
                )

                signature_request.full_clean()
                signature_request.save()

                for version in normalized_versions:
                    request_document = SignatureRequestDocument(
                        signature_request=signature_request,
                        source_version=version,
                        status=(
                            SignatureRequestDocument.Status.DRAFT
                        ),
                    )

                    request_document.full_clean()
                    request_document.save()

                    prepared_document = (
                        self.artifact_service.prepare_pdf(
                            request_document=request_document,
                        )
                    )

                    stored_artifact_keys.append(
                        prepared_document.prepared_storage_key
                    )

                    prepared_document.status = (
                        SignatureRequestDocument.Status.READY
                    )

                    prepared_document.full_clean()

                    prepared_document.save(
                        update_fields=[
                            "status",
                            "updated_at",
                        ]
                    )

                for recipient in normalized_recipients:
                    signature_recipient = (
                        SignatureRequestRecipient(
                            signature_request=signature_request,
                            user=recipient.user,
                            full_name=recipient.full_name,
                            email=recipient.email,
                            signing_order=recipient.signing_order,
                            status=(
                                SignatureRequestRecipient
                                .Status.PENDING
                            ),
                        )
                    )

                    signature_recipient.full_clean()
                    signature_recipient.save()

                return signature_request

        except Exception:
            self._delete_artifacts(stored_artifact_keys)
            raise

    def send_draft(
        self,
        *,
        signature_request: SignatureRequest,
    ) -> SignatureRequest:
        """
        Envoie un brouillon vers le fournisseur de signature configuré.

        La demande reste liée à l'ExternalIntegration sélectionnée lors
        de sa création, même si les priorités de configuration changent
        par la suite.
        """

        with transaction.atomic():
            locked_request = (
                SignatureRequest.objects
                .select_for_update()
                .select_related(
                    "external_integration",
                    "external_integration__provider",
                )
                .get(pk=signature_request.pk)
            )

            if (
                locked_request.status
                != SignatureRequest.Status.DRAFT
            ):
                raise ValueError(
                    "Seule une demande de signature en brouillon "
                    "peut être envoyée."
                )

            request_documents = tuple(
                SignatureRequestDocument.objects
                .select_for_update()
                .select_related(
                    "source_version",
                    "source_version__document",
                )
                .filter(signature_request=locked_request)
                .order_by("created_at")
            )

            if not request_documents:
                raise ValueError(
                    "La demande ne contient aucun document."
                )

            for request_document in request_documents:
                if (
                    request_document.status
                    != SignatureRequestDocument.Status.READY
                ):
                    raise ValueError(
                        "Tous les documents doivent être préparés "
                        "avant l'envoi en signature."
                    )

            request_recipients = tuple(
                SignatureRequestRecipient.objects
                .select_for_update()
                .filter(signature_request=locked_request)
                .order_by(
                    "signing_order",
                    "email",
                )
            )

            if not request_recipients:
                raise ValueError(
                    "La demande ne contient aucun signataire."
                )

            integration = self._get_signature_integration(
                locked_request.external_integration
            )

            with ExitStack() as stack:
                document_submissions = tuple(
                    SignatureDocumentSubmission(
                        request_document_id=str(
                            request_document.pk
                        ),
                        filename=(
                            request_document.prepared_filename
                        ),
                        content=stack.enter_context(
                            self.artifact_service.open_prepared_pdf(
                                request_document=request_document,
                            )
                        ),
                        checksum=(
                            request_document.prepared_checksum
                        ),
                    )
                    for request_document in request_documents
                )

                recipient_submissions = tuple(
                    SignatureRecipientSubmission(
                        recipient_id=str(recipient.pk),
                        full_name=recipient.full_name,
                        email=recipient.email,
                        signing_order=recipient.signing_order,
                    )
                    for recipient in request_recipients
                )

                submission = (
                    integration.create_signature_request(
                        external_integration=(
                            locked_request
                            .external_integration
                        ),
                        signature_request=locked_request,
                        documents=document_submissions,
                        recipients=recipient_submissions,
                    )
                )

            provider_request_id = (
                submission.provider_request_id.strip()
            )

            if not provider_request_id:
                raise ValueError(
                    "Le fournisseur n'a retourné aucun identifiant "
                    "de demande de signature."
                )

            locked_request.provider_request_id = (
                provider_request_id
            )
            locked_request.status = (
                SignatureRequest.Status.SENT
            )
            locked_request.sent_at = timezone.now()

            locked_request.full_clean()

            locked_request.save(
                update_fields=[
                    "provider_request_id",
                    "status",
                    "sent_at",
                    "updated_at",
                ]
            )

            for request_document in request_documents:
                request_document.status = (
                    SignatureRequestDocument.Status.SENT
                )

                request_document.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            for recipient in request_recipients:
                recipient.status = (
                    SignatureRequestRecipient.Status.SENT
                )

                recipient.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

            return locked_request

    @staticmethod
    def _validate_external_integration(
        *,
        project: Project,
        external_integration: ExternalIntegration,
    ) -> None:
        if (
            external_integration.client_environment.company_id
            != project.company_id
        ):
            raise ValueError(
                "L'intégration de signature doit appartenir "
                "à l'environnement client du projet."
            )

        if not external_integration.is_active:
            raise ValueError(
                "L'intégration de signature sélectionnée est inactive."
            )

        if (
            external_integration.service_type.code
            != "SIGNATURE"
        ):
            raise ValueError(
                "L'intégration sélectionnée n'est pas un "
                "service de signature électronique."
            )

        if (
            external_integration.connection_status.code
            != "CONNECTED"
        ):
            raise ValueError(
                "L'intégration de signature sélectionnée "
                "n'est pas connectée."
            )

    @staticmethod
    def _validate_versions(
        *,
        project: Project,
        versions: tuple[DocumentVersion, ...],
    ) -> None:
        version_ids = set()

        for version in versions:
            if version.pk in version_ids:
                raise ValueError(
                    "Un même document ne peut pas être ajouté "
                    "plusieurs fois à la demande."
                )

            version_ids.add(version.pk)

            if version.document.project_id != project.pk:
                raise ValueError(
                    "Tous les documents à signer doivent "
                    "appartenir au projet courant."
                )

            if not (
                version.mime_type.lower() == "application/pdf"
                or version.original_filename.lower().endswith(
                    ".pdf"
                )
            ):
                raise ValueError(
                    "Seuls les documents PDF peuvent être envoyés "
                    "en signature pour le moment."
                )

    @staticmethod
    def _normalize_recipients(
        recipients: Sequence[SignatureRecipientInput],
    ) -> tuple[SignatureRecipientInput, ...]:
        if not recipients:
            raise ValueError(
                "Sélectionnez au moins un signataire."
            )

        normalized_recipients = []
        emails = set()

        for recipient in recipients:
            full_name = recipient.full_name.strip()
            email = recipient.email.strip().lower()

            if not full_name:
                raise ValueError(
                    "Le nom de chaque signataire est obligatoire."
                )

            if not email:
                raise ValueError(
                    "L'adresse e-mail de chaque signataire "
                    "est obligatoire."
                )

            if recipient.signing_order < 1:
                raise ValueError(
                    "L'ordre de signature doit être supérieur à zéro."
                )

            if email in emails:
                raise ValueError(
                    "Un signataire ne peut apparaître qu'une "
                    "seule fois dans la demande."
                )

            emails.add(email)

            normalized_recipients.append(
                SignatureRecipientInput(
                    full_name=full_name,
                    email=email,
                    signing_order=recipient.signing_order,
                    user=recipient.user,
                )
            )

        return tuple(
            sorted(
                normalized_recipients,
                key=lambda recipient: (
                    recipient.signing_order,
                    recipient.email,
                ),
            )
        )

    def _get_signature_integration(
        self,
        external_integration: ExternalIntegration,
    ) -> SignatureIntegration:
        provider_code = external_integration.provider.code

        try:
            integration = self.integration_registry.get(
                provider_code
            )
        except LookupError as exc:
            raise ValueError(
                "Aucun adaptateur Easy Projet n'est installé "
                f"pour le fournisseur {provider_code}."
            ) from exc

        if not isinstance(
            integration,
            SignatureIntegration,
        ):
            raise ValueError(
                f"Le fournisseur {provider_code} ne fournit pas "
                "de service de signature électronique."
            )

        return integration

    def _delete_artifacts(
        self,
        storage_keys: list[str],
    ) -> None:
        """
        Nettoie les copies physiques si la transaction de création
        de brouillon échoue.
        """

        for storage_key in storage_keys:
            try:
                if self.artifact_service.storage.exists(
                    storage_key
                ):
                    self.artifact_service.storage.delete(
                        storage_key
                    )
            except Exception:
                # L'erreur de création reste prioritaire.
                pass