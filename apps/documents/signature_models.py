

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from apps.integrations.models import ExternalIntegration
from apps.projects.models import Project
from apps.users.models import User
from common.constants.document import (
    DOCUMENT_CHECKSUM_LENGTH,
    DOCUMENT_MIME_TYPE_LENGTH,
    DOCUMENT_STORAGE_KEY_LENGTH,
)
from common.constants.signature import (
    SIGNATURE_EMAIL_LENGTH,
    SIGNATURE_EVENT_TYPE_LENGTH,
    SIGNATURE_FILENAME_LENGTH,
    SIGNATURE_NAME_LENGTH,
    SIGNATURE_PROVIDER_IDENTIFIER_LENGTH,
    SIGNATURE_REQUEST_TITLE_LENGTH,
)
from common.models import TimeStampedModel


class SignatureRequest(TimeStampedModel):
    """
    Dossier de signature électronique.

    Une demande peut contenir un ou plusieurs documents et
    un ou plusieurs signataires internes ou externes.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "DRAFT",
            "Brouillon",
        )
        SENT = (
            "SENT",
            "Envoyée",
        )
        PARTIALLY_SIGNED = (
            "PARTIALLY_SIGNED",
            "Partiellement signée",
        )
        COMPLETED = (
            "COMPLETED",
            "Signée",
        )
        REFUSED = (
            "REFUSED",
            "Refusée",
        )
        CANCELLED = (
            "CANCELLED",
            "Annulée",
        )
        EXPIRED = (
            "EXPIRED",
            "Expirée",
        )
        FAILED = (
            "FAILED",
            "En erreur",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="signature_requests",
        verbose_name="Projet",
    )

    external_integration = models.ForeignKey(
        ExternalIntegration,
        on_delete=models.PROTECT,
        related_name="signature_requests",
        verbose_name="Intégration de signature",
    )

    title = models.CharField(
        max_length=SIGNATURE_REQUEST_TITLE_LENGTH,
        verbose_name="Intitulé",
    )

    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="État",
    )

    provider_request_id = models.CharField(
        max_length=SIGNATURE_PROVIDER_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name="Identifiant de demande prestataire",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Envoyée le",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Terminée le",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expire le",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_signature_requests",
        verbose_name="Créée par",
    )

    def clean(self) -> None:
        """
        Vérifie que l'intégration appartient à la société
        du projet concerné.
        """

        super().clean()

        if (
            self.project_id is not None
            and self.external_integration_id is not None
            and self.external_integration
            .client_environment.company_id
            != self.project.company_id
        ):
            raise ValidationError(
                {
                    "external_integration": (
                        "L'intégration de signature doit appartenir "
                        "à l'environnement client de la société "
                        "du projet."
                    ),
                }
            )

    @property
    def is_finalized(self) -> bool:
        """
        Indique si la demande ne peut plus recevoir
        de signature.
        """

        return self.status in {
            self.Status.COMPLETED,
            self.Status.REFUSED,
            self.Status.CANCELLED,
            self.Status.EXPIRED,
            self.Status.FAILED,
        }

    def save(self, *args, **kwargs) -> None:
        self.title = self.title.strip()
        self.provider_request_id = (
            self.provider_request_id.strip()
        )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "signature_request"
        ordering = [
            "-created_at",
            "title",
        ]
        verbose_name = "Demande de signature"
        verbose_name_plural = "Demandes de signature"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "external_integration",
                    "provider_request_id",
                ],
                condition=~models.Q(
                    provider_request_id="",
                ),
                name=(
                    "uniq_signature_request_provider_identifier"
                ),
            ),
        ]

    def __str__(self) -> str:
        return self.title


class SignatureRequestDocument(TimeStampedModel):
    """
    Document inclus dans une demande de signature.

    La version source reste inchangée. Les fichiers préparé
    et signé sont des artefacts immuables de la transaction.
    """

    class Status(models.TextChoices):
        DRAFT = (
            "DRAFT",
            "Brouillon",
        )
        READY = (
            "READY",
            "Prêt à envoyer",
        )
        SENT = (
            "SENT",
            "Envoyé",
        )
        SIGNED = (
            "SIGNED",
            "Signé",
        )
        REFUSED = (
            "REFUSED",
            "Refusé",
        )
        FAILED = (
            "FAILED",
            "En erreur",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    signature_request = models.ForeignKey(
        SignatureRequest,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Demande de signature",
    )

    source_version = models.ForeignKey(
        "DocumentVersion",
        on_delete=models.PROTECT,
        related_name="signature_request_documents",
        verbose_name="Version source",
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="État",
    )

    provider_document_id = models.CharField(
        max_length=SIGNATURE_PROVIDER_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name="Identifiant de document prestataire",
    )

    prepared_storage_key = models.CharField(
        max_length=DOCUMENT_STORAGE_KEY_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Clé du PDF préparé",
    )

    prepared_filename = models.CharField(
        max_length=SIGNATURE_FILENAME_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Nom du PDF préparé",
    )

    prepared_mime_type = models.CharField(
        max_length=DOCUMENT_MIME_TYPE_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Type MIME du PDF préparé",
    )

    prepared_file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Taille du PDF préparé",
    )

    prepared_checksum = models.CharField(
        max_length=DOCUMENT_CHECKSUM_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Empreinte du PDF préparé",
    )

    prepared_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Préparé le",
    )

    signed_storage_key = models.CharField(
        max_length=DOCUMENT_STORAGE_KEY_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Clé du PDF signé",
    )

    signed_filename = models.CharField(
        max_length=SIGNATURE_FILENAME_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Nom du PDF signé",
    )

    signed_mime_type = models.CharField(
        max_length=DOCUMENT_MIME_TYPE_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Type MIME du PDF signé",
    )

    signed_file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Taille du PDF signé",
    )

    signed_checksum = models.CharField(
        max_length=DOCUMENT_CHECKSUM_LENGTH,
        blank=True,
        editable=False,
        verbose_name="Empreinte du PDF signé",
    )

    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Signé le",
    )

    def clean(self) -> None:
        """
        Vérifie que la version source appartient au même projet
        que la demande de signature.
        """

        super().clean()

        if (
            self.signature_request_id is not None
            and self.source_version_id is not None
            and self.source_version.document.project_id
            != self.signature_request.project_id
        ):
            raise ValidationError(
                {
                    "source_version": (
                        "La version source doit appartenir au même "
                        "projet que la demande de signature."
                    ),
                }
            )

    @property
    def has_prepared_pdf(self) -> bool:
        """
        Indique si l'artefact PDF envoyé au prestataire existe.
        """

        return bool(self.prepared_storage_key)

    @property
    def has_signed_pdf(self) -> bool:
        """
        Indique si le prestataire a retourné le PDF signé.
        """

        return bool(self.signed_storage_key)

    def save(self, *args, **kwargs) -> None:
        self.provider_document_id = (
            self.provider_document_id.strip()
        )
        self.prepared_storage_key = (
            self.prepared_storage_key.strip()
        )
        self.prepared_filename = (
            self.prepared_filename.strip()
        )
        self.prepared_mime_type = (
            self.prepared_mime_type.strip().lower()
        )
        self.prepared_checksum = (
            self.prepared_checksum.strip().lower()
        )
        self.signed_storage_key = (
            self.signed_storage_key.strip()
        )
        self.signed_filename = (
            self.signed_filename.strip()
        )
        self.signed_mime_type = (
            self.signed_mime_type.strip().lower()
        )
        self.signed_checksum = (
            self.signed_checksum.strip().lower()
        )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "signature_request_document"
        ordering = [
            "created_at",
        ]
        verbose_name = "Document à signer"
        verbose_name_plural = "Documents à signer"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "signature_request",
                    "source_version",
                ],
                name=(
                    "uniq_signature_request_source_version"
                ),
            ),
        ]

    def __str__(self) -> str:
        return str(self.source_version)


class SignatureRequestRecipient(TimeStampedModel):
    """
    Signataire interne ou externe d'une demande.
    """

    class Status(models.TextChoices):
        PENDING = (
            "PENDING",
            "En attente",
        )
        SENT = (
            "SENT",
            "Invitation envoyée",
        )
        VIEWED = (
            "VIEWED",
            "Consulté",
        )
        SIGNED = (
            "SIGNED",
            "Signé",
        )
        REFUSED = (
            "REFUSED",
            "Refusé",
        )
        EXPIRED = (
            "EXPIRED",
            "Expiré",
        )
        FAILED = (
            "FAILED",
            "En erreur",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    signature_request = models.ForeignKey(
        SignatureRequest,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Demande de signature",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="signature_request_recipients",
        null=True,
        blank=True,
        verbose_name="Utilisateur interne",
    )

    full_name = models.CharField(
        max_length=SIGNATURE_NAME_LENGTH,
        verbose_name="Nom du signataire",
    )

    email = models.EmailField(
        max_length=SIGNATURE_EMAIL_LENGTH,
        verbose_name="E-mail du signataire",
    )

    signing_order = models.PositiveIntegerField(
        default=1,
        verbose_name="Ordre de signature",
        help_text=(
            "Les signataires du même ordre peuvent signer "
            "en parallèle."
        ),
    )

    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="État",
    )

    provider_recipient_id = models.CharField(
        max_length=SIGNATURE_PROVIDER_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name="Identifiant de signataire prestataire",
    )

    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Signé le",
    )

    def save(self, *args, **kwargs) -> None:
        self.full_name = self.full_name.strip()
        self.email = self.email.strip().lower()
        self.provider_recipient_id = (
            self.provider_recipient_id.strip()
        )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "signature_request_recipient"
        ordering = [
            "signing_order",
            "full_name",
        ]
        verbose_name = "Signataire"
        verbose_name_plural = "Signataires"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "signature_request",
                    "email",
                ],
                name=(
                    "uniq_signature_request_recipient_email"
                ),
            ),
        ]

    def __str__(self) -> str:
        return self.full_name


class SignatureEvent(TimeStampedModel):
    """
    Événement reçu ou enregistré durant une demande de signature.

    Les événements du prestataire sont conservés afin de disposer
    d'une trace complète et de rendre les webhooks idempotents.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    signature_request = models.ForeignKey(
        SignatureRequest,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Demande de signature",
    )

    recipient = models.ForeignKey(
        SignatureRequestRecipient,
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True,
        verbose_name="Signataire",
    )

    event_type = models.CharField(
        max_length=SIGNATURE_EVENT_TYPE_LENGTH,
        verbose_name="Type d'événement",
    )

    provider_event_id = models.CharField(
        max_length=SIGNATURE_PROVIDER_IDENTIFIER_LENGTH,
        blank=True,
        verbose_name="Identifiant d'événement prestataire",
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données de l'événement",
    )

    def save(self, *args, **kwargs) -> None:
        self.event_type = self.event_type.strip().upper()
        self.provider_event_id = (
            self.provider_event_id.strip()
        )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "signature_event"
        ordering = [
            "created_at",
        ]
        verbose_name = "Événement de signature"
        verbose_name_plural = "Événements de signature"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "signature_request",
                    "provider_event_id",
                ],
                condition=~models.Q(
                    provider_event_id="",
                ),
                name=(
                    "uniq_signature_event_provider_identifier"
                ),
            ),
        ]

    def __str__(self) -> str:
        return self.event_type