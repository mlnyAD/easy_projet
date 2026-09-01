

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from apps.documents.models import DocumentVersion
from apps.projects.models import (
    Project,
    ProjectExternalParticipant,
)
from apps.users.models import User
from common.constants.communication import (
    COMMUNICATION_ATTACHMENT_FILENAME_LENGTH,
    COMMUNICATION_ATTACHMENT_MIME_TYPE_LENGTH,
    COMMUNICATION_CONVERSATION_TITLE_LENGTH,
    COMMUNICATION_EMAIL_LENGTH,
    COMMUNICATION_ERROR_DETAILS_LENGTH,
    COMMUNICATION_SENDER_NAME_LENGTH,
    COMMUNICATION_SUBJECT_LENGTH,
)
from common.models import TimeStampedModel


def communication_attachment_upload_to(
    instance,
    filename: str,
) -> str:
    """
    Construit le chemin de stockage d'une pièce jointe
    propre à une communication.

    Le nom fourni par le poste utilisateur est réduit
    à son seul nom de fichier.
    """

    safe_filename = Path(
        filename
    ).name

    return (
        f"communications/"
        f"{instance.message_id}/"
        f"{safe_filename}"
    )


class CommunicationConversation(
    TimeStampedModel
):
    """
    Fil de communication rattaché à un projet.

    Une conversation constitue le conteneur logique
    des messages échangés autour d'un projet.

    La V1 pourra utiliser principalement un fil global
    par projet. Le modèle autorise néanmoins plusieurs
    conversations afin de ne pas limiter les évolutions
    futures.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="communication_conversations",
        verbose_name="Projet",
    )

    title = models.CharField(
        max_length=(
            COMMUNICATION_CONVERSATION_TITLE_LENGTH
        ),
        blank=True,
        verbose_name="Sujet",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name=(
            "created_communication_conversations"
        ),
        verbose_name="Créée par",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        self.title = (
            self.title
            or ""
        ).strip()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "communication_conversation"

        ordering = [
            "project",
            "created_at",
        ]

        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def __str__(self) -> str:
        if self.title:
            return (
                f"{self.project.reference} - "
                f"{self.title}"
            )

        return (
            f"{self.project.reference} - "
            "Communications"
        )


class CommunicationMessage(
    TimeStampedModel
):
    """
    Message appartenant à une conversation.

    Le contenu du message est indépendant du canal
    utilisé pour le distribuer.

    Une même communication pourra ainsi être :
    - affichée dans la messagerie interne ;
    - envoyée par email ;
    - transmise ultérieurement à l'application mobile.
    """

    class Origin(models.TextChoices):
        INTERNAL = (
            "INTERNAL",
            "Easy Projet",
        )

        IMPORTED_EMAIL = (
            "IMPORTED_EMAIL",
            "Email importé",
        )

        MOBILE = (
            "MOBILE",
            "Application mobile",
        )

        SYSTEM = (
            "SYSTEM",
            "Système",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    conversation = models.ForeignKey(
        CommunicationConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Conversation",
    )

    origin = models.CharField(
        max_length=20,
        choices=Origin.choices,
        default=Origin.INTERNAL,
        verbose_name="Origine",
    )

    # ------------------------------------------------------------------
    # Auteur Easy Projet
    # ------------------------------------------------------------------

    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="communication_messages",
        null=True,
        blank=True,
        verbose_name="Auteur",
    )

    # ------------------------------------------------------------------
    # Expéditeur externe
    #
    # Utilisé notamment pour un email que l'utilisateur
    # rattache volontairement au projet.
    # ------------------------------------------------------------------

    sender_name = models.CharField(
        max_length=COMMUNICATION_SENDER_NAME_LENGTH,
        blank=True,
        verbose_name="Nom de l'expéditeur",
    )

    sender_email = models.EmailField(
        max_length=COMMUNICATION_EMAIL_LENGTH,
        blank=True,
        verbose_name="Adresse de l'expéditeur",
    )

    # ------------------------------------------------------------------
    # Import
    #
    # L'utilisateur ayant volontairement intégré un email
    # extérieur dans Easy Projet.
    # ------------------------------------------------------------------

    imported_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="imported_communication_messages",
        null=True,
        blank=True,
        verbose_name="Importé par",
    )
    
    subject = models.CharField(
        max_length=COMMUNICATION_SUBJECT_LENGTH,
        blank=True,
        verbose_name="Objet",
    )

    body = models.TextField(
        blank=True,
        verbose_name="Message",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    def clean(self) -> None:
        """
        Vérifie la cohérence de l'origine du message.
        """

        super().clean()

        if (
            self.origin
            == self.Origin.INTERNAL
            and self.author_id is None
        ):
            raise ValidationError(
                {
                    "author": (
                        "Un message Easy Projet doit "
                        "avoir un auteur."
                    ),
                }
            )

        if (
            self.origin
            == self.Origin.IMPORTED_EMAIL
        ):
            errors = {}

            if not self.sender_email:
                errors["sender_email"] = (
                    "L'adresse de l'expéditeur "
                    "du mail doit être renseignée."
                )

            if self.imported_by_id is None:
                errors["imported_by"] = (
                    "L'utilisateur ayant importé "
                    "le mail doit être renseigné."
                )

            if errors:
                raise ValidationError(
                    errors
                )

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        self.sender_name = (
            self.sender_name
            or ""
        ).strip()

        self.sender_email = (
            self.sender_email
            or ""
        ).strip().lower()

        self.subject = (
            self.subject
            or ""
        ).strip()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "communication_message"

        ordering = [
            "created_at",
        ]

        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self) -> str:
        if self.author_id is not None:
            sender = str(
                self.author
            )
        elif self.sender_name:
            sender = self.sender_name
        elif self.sender_email:
            sender = self.sender_email
        else:
            sender = "Système"

        return (
            f"{self.conversation.project.reference} "
            f"- {sender}"
        )


class CommunicationMessageRecipient(
    TimeStampedModel
):
    """
    Distribution d'un message à un destinataire.

    Le destinataire et le canal sont volontairement
    séparés du message lui-même.

    Un même message peut ainsi être distribué par
    plusieurs canaux.
    """

    class Channel(models.TextChoices):
        INTERNAL = (
            "INTERNAL",
            "Messagerie interne",
        )

        EMAIL = (
            "EMAIL",
            "Email",
        )

        MOBILE = (
            "MOBILE",
            "Application mobile",
        )

    class Status(models.TextChoices):
        PENDING = (
            "PENDING",
            "En attente",
        )

        SENT = (
            "SENT",
            "Envoyé",
        )

        DELIVERED = (
            "DELIVERED",
            "Distribué",
        )

        READ = (
            "READ",
            "Lu",
        )

        FAILED = (
            "FAILED",
            "Échec",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    message = models.ForeignKey(
        CommunicationMessage,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Message",
    )

    # ------------------------------------------------------------------
    # Destinataire interne
    # ------------------------------------------------------------------

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="received_communication_messages",
        null=True,
        blank=True,
        verbose_name="Utilisateur",
    )

    # ------------------------------------------------------------------
    # Destinataire externe rattaché au projet
    # ------------------------------------------------------------------

    external_participant = models.ForeignKey(
        ProjectExternalParticipant,
        on_delete=models.PROTECT,
        related_name="communication_messages",
        null=True,
        blank=True,
        verbose_name="Intervenant externe",
    )

    # ------------------------------------------------------------------
    # Adresse réellement utilisée.
    #
    # Elle constitue un instantané de la destination,
    # notamment pour assurer la traçabilité d'un email.
    # ------------------------------------------------------------------

    destination_email = models.EmailField(
        max_length=COMMUNICATION_EMAIL_LENGTH,
        blank=True,
        verbose_name="Adresse de destination",
    )
    class Purpose(models.TextChoices):
        ACTION = (
            "ACTION",
            "Pour action",
        )

        INFORMATION = (
            "INFORMATION",
            "Pour information",
        )
        
    purpose = models.CharField(
        max_length=20,
        choices=Purpose.choices,
        default=Purpose.INFORMATION,
        verbose_name="Type de diffusion",
    )
        
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        verbose_name="Canal",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="État",
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Envoyé le",
    )

    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Distribué le",
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Lu le",
    )

    error_details = models.TextField(
        max_length=COMMUNICATION_ERROR_DETAILS_LENGTH,
        blank=True,
        verbose_name="Détail de l'erreur",
    )

    def clean(self) -> None:
        """
        Vérifie la cohérence du destinataire et du canal.
        """

        super().clean()

        errors = {}

        recipient_count = sum(
            (
                self.user_id is not None,
                self.external_participant_id
                is not None,
            )
        )

        if recipient_count == 0:
            errors["user"] = (
                "Un destinataire doit être renseigné."
            )

        if recipient_count > 1:
            errors["user"] = (
                "Une distribution ne peut avoir "
                "qu'un seul destinataire."
            )

        if (
            self.channel
            == self.Channel.INTERNAL
            and self.user_id is None
        ):
            errors["channel"] = (
                "La messagerie interne nécessite "
                "un utilisateur Easy Projet."
            )

        if (
            self.channel
            == self.Channel.MOBILE
            and self.user_id is None
        ):
            errors["channel"] = (
                "Le canal mobile nécessite "
                "un utilisateur Easy Projet."
            )

        if (
            self.channel
            == self.Channel.EMAIL
            and not self.destination_email
        ):
            errors["destination_email"] = (
                "Une adresse email de destination "
                "doit être renseignée."
            )

        if (
            self.external_participant_id
            is not None
            and self.message_id is not None
            and (
                self.external_participant.project_id
                != self.message.conversation.project_id
            )
        ):
            errors["external_participant"] = (
                "L'intervenant externe doit appartenir "
                "au même projet que la conversation."
            )

        if errors:
            raise ValidationError(
                errors
            )

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        self.destination_email = (
            self.destination_email
            or ""
        ).strip().lower()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "communication_message_recipient"

        ordering = [
            "message",
            "created_at",
        ]

        verbose_name = "Destinataire"
        verbose_name_plural = "Destinataires"

    def __str__(self) -> str:
        if self.user_id is not None:
            recipient = str(
                self.user
            )
        elif self.external_participant_id is not None:
            recipient = str(
                self.external_participant
            )
        else:
            recipient = self.destination_email

        return (
            f"{recipient} - "
            f"{self.get_channel_display()}"
        )


class CommunicationMessageAttachment(
    TimeStampedModel
):
    """
    Pièce jointe à une communication.

    Une pièce jointe peut être :

    - un fichier directement déposé dans la communication ;
    - une référence à une version documentaire déjà enregistrée
      dans la GED Easy Projet.

    Aucun type de fichier n'est interdit par ce modèle.
    La capacité d'aperçu est indépendante de la capacité
    de stockage et de téléchargement.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    message = models.ForeignKey(
        CommunicationMessage,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Message",
    )

    uploaded_file = models.FileField(
        upload_to=communication_attachment_upload_to,
        null=True,
        blank=True,
        verbose_name="Fichier",
    )

    document_version = models.ForeignKey(
        DocumentVersion,
        on_delete=models.PROTECT,
        related_name="communication_attachments",
        null=True,
        blank=True,
        verbose_name="Version documentaire",
    )

    original_filename = models.CharField(
        max_length=(
            COMMUNICATION_ATTACHMENT_FILENAME_LENGTH
        ),
        blank=True,
        verbose_name="Nom du fichier",
    )

    mime_type = models.CharField(
        max_length=(
            COMMUNICATION_ATTACHMENT_MIME_TYPE_LENGTH
        ),
        blank=True,
        verbose_name="Type MIME",
    )

    file_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
        verbose_name="Taille du fichier",
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="communication_attachments",
        verbose_name="Déposé par",
    )

    def clean(self) -> None:
        """
        Vérifie qu'une pièce jointe possède une source unique.
        """

        super().clean()

        has_uploaded_file = bool(
            self.uploaded_file
        )

        has_document_version = (
            self.document_version_id
            is not None
        )

        if (
            has_uploaded_file
            == has_document_version
        ):
            raise ValidationError(
                (
                    "Une pièce jointe doit référencer "
                    "soit un fichier déposé, soit une "
                    "version documentaire, mais pas les deux."
                )
            )

        if (
            self.document_version_id
            is not None
            and self.message_id is not None
            and (
                self.document_version
                .document
                .project_id
                != self.message
                .conversation
                .project_id
            )
        ):
            raise ValidationError(
                {
                    "document_version": (
                        "Le document joint doit appartenir "
                        "au même projet que la conversation."
                    ),
                }
            )

    def save(
        self,
        *args,
        **kwargs,
    ) -> None:
        if self.uploaded_file:
            if not self.original_filename:
                self.original_filename = (
                    Path(
                        self.uploaded_file.name
                    ).name
                )

            if self.file_size is None:
                try:
                    self.file_size = (
                        self.uploaded_file.size
                    )
                except (
                    AttributeError,
                    OSError,
                ):
                    pass

        elif self.document_version_id is not None:
            if not self.original_filename:
                self.original_filename = (
                    self.document_version
                    .original_filename
                )

            if not self.mime_type:
                self.mime_type = (
                    self.document_version
                    .mime_type
                )

            if self.file_size is None:
                self.file_size = (
                    self.document_version
                    .file_size
                )

        self.original_filename = (
            self.original_filename
            or ""
        ).strip()

        self.mime_type = (
            self.mime_type
            or ""
        ).strip().lower()

        super().save(
            *args,
            **kwargs,
        )

    class Meta:
        db_table = "communication_message_attachment"

        ordering = [
            "message",
            "created_at",
        ]

        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"

    def __str__(self) -> str:
        return (
            self.original_filename
            or "Pièce jointe"
        )