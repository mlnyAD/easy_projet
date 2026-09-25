from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from apps.documents.models import DocumentVersion
from apps.projects.models import Project, ProjectExternalParticipant
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


def communication_attachment_upload_to(instance, filename: str) -> str:
    return f"communications/{instance.message_id}/{Path(filename).name}"


class CommunicationConversation(TimeStampedModel):
    """Fil de messagerie personnel, éventuellement contextualisé par des projets."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name="Identifiant")
    projects = models.ManyToManyField(
        Project,
        related_name="communication_conversations",
        blank=True,
        verbose_name="Projets liés",
    )
    title = models.CharField(
        max_length=COMMUNICATION_CONVERSATION_TITLE_LENGTH,
        blank=True,
        verbose_name="Sujet",
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_communication_conversations",
        verbose_name="Créée par",
    )
    is_active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        db_table = "communication_conversation"
        ordering = ["-updated_at", "-created_at"]
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

    def save(self, *args, **kwargs) -> None:
        self.title = (self.title or "").strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title or "Conversation"


class CommunicationMessage(TimeStampedModel):
    class Origin(models.TextChoices):
        INTERNAL = "INTERNAL", "Easy Projet"
        IMPORTED_EMAIL = "IMPORTED_EMAIL", "Email importé"
        MOBILE = "MOBILE", "Application mobile"
        SYSTEM = "SYSTEM", "Système"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name="Identifiant")
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
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="communication_messages",
        null=True,
        blank=True,
        verbose_name="Auteur",
    )
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
    body = models.TextField(blank=True, verbose_name="Message")
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        db_table = "communication_message"
        ordering = ["created_at"]
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def clean(self) -> None:
        super().clean()
        errors = {}
        if self.origin == self.Origin.INTERNAL and self.author_id is None:
            errors["author"] = "Un message Easy Projet doit avoir un auteur."
        if self.origin == self.Origin.IMPORTED_EMAIL:
            if not self.sender_email:
                errors["sender_email"] = "L'adresse de l'expéditeur doit être renseignée."
            if self.imported_by_id is None:
                errors["imported_by"] = "L'utilisateur ayant importé le mail doit être renseigné."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.sender_name = (self.sender_name or "").strip()
        self.sender_email = (self.sender_email or "").strip().lower()
        self.subject = (self.subject or "").strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.conversation} - {self.subject or self.author or 'Système'}"


class CommunicationMessageRecipient(TimeStampedModel):
    class Channel(models.TextChoices):
        INTERNAL = "INTERNAL", "Messagerie interne"
        EMAIL = "EMAIL", "Email"
        MOBILE = "MOBILE", "Application mobile"

    class Status(models.TextChoices):
        PENDING = "PENDING", "En attente"
        SENT = "SENT", "Envoyé"
        DELIVERED = "DELIVERED", "Distribué"
        READ = "READ", "Lu"
        FAILED = "FAILED", "Échec"

    class Purpose(models.TextChoices):
        ACTION = "ACTION", "Pour action"
        INFORMATION = "INFORMATION", "Pour information"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name="Identifiant")
    message = models.ForeignKey(CommunicationMessage, on_delete=models.CASCADE, related_name="recipients", verbose_name="Message")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="received_communication_messages", null=True, blank=True, verbose_name="Utilisateur")
    external_participant = models.ForeignKey(ProjectExternalParticipant, on_delete=models.PROTECT, related_name="communication_messages", null=True, blank=True, verbose_name="Intervenant externe")
    destination_email = models.EmailField(max_length=COMMUNICATION_EMAIL_LENGTH, blank=True, verbose_name="Adresse de destination")
    purpose = models.CharField(max_length=20, choices=Purpose.choices, default=Purpose.INFORMATION, verbose_name="Type de diffusion")
    channel = models.CharField(max_length=20, choices=Channel.choices, verbose_name="Canal")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="État")
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Envoyé le")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Distribué le")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Lu le")
    error_details = models.TextField(max_length=COMMUNICATION_ERROR_DETAILS_LENGTH, blank=True, verbose_name="Détail de l'erreur")

    class Meta:
        db_table = "communication_message_recipient"
        ordering = ["message", "created_at"]
        verbose_name = "Destinataire"
        verbose_name_plural = "Destinataires"

    def clean(self) -> None:
        super().clean()
        errors = {}
        identified_count = sum((self.user_id is not None, self.external_participant_id is not None))
        direct_email = self.channel == self.Channel.EMAIL and bool(self.destination_email)
        if identified_count == 0 and not direct_email:
            errors["user"] = "Un destinataire ou une adresse email doit être renseigné."
        if identified_count > 1:
            errors["user"] = "Une distribution ne peut avoir qu'un seul destinataire."
        if self.channel in {self.Channel.INTERNAL, self.Channel.MOBILE} and self.user_id is None:
            errors["channel"] = "Ce canal nécessite un utilisateur Easy Projet."
        if self.channel == self.Channel.EMAIL and not self.destination_email:
            errors["destination_email"] = "Une adresse email de destination doit être renseignée."
        if self.external_participant_id and self.message_id:
            if not self.message.conversation.projects.filter(pk=self.external_participant.project_id).exists():
                errors["external_participant"] = "L'intervenant externe doit appartenir à l'un des projets liés à la conversation."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs) -> None:
        self.destination_email = (self.destination_email or "").strip().lower()
        super().save(*args, **kwargs)


class CommunicationMessageAttachment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False, verbose_name="Identifiant")
    message = models.ForeignKey(CommunicationMessage, on_delete=models.CASCADE, related_name="attachments", verbose_name="Message")
    uploaded_file = models.FileField(upload_to=communication_attachment_upload_to, null=True, blank=True, verbose_name="Fichier")
    document_version = models.ForeignKey(DocumentVersion, on_delete=models.PROTECT, related_name="communication_attachments", null=True, blank=True, verbose_name="Version documentaire")
    original_filename = models.CharField(max_length=COMMUNICATION_ATTACHMENT_FILENAME_LENGTH, blank=True, verbose_name="Nom du fichier")
    mime_type = models.CharField(max_length=COMMUNICATION_ATTACHMENT_MIME_TYPE_LENGTH, blank=True, verbose_name="Type MIME")
    file_size = models.PositiveBigIntegerField(null=True, blank=True, verbose_name="Taille du fichier")
    uploaded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="communication_attachments", verbose_name="Déposé par")

    class Meta:
        db_table = "communication_message_attachment"
        ordering = ["message", "created_at"]
        verbose_name = "Pièce jointe de communication"
        verbose_name_plural = "Pièces jointes de communication"

    def clean(self) -> None:
        super().clean()
        if bool(self.uploaded_file) == (self.document_version_id is not None):
            raise ValidationError("Une pièce jointe doit référencer soit un fichier déposé, soit une version documentaire, mais pas les deux.")
        if self.document_version_id and self.message_id:
            project_id = self.document_version.document.project_id
            if not self.message.conversation.projects.filter(pk=project_id).exists():
                raise ValidationError({"document_version": "Le document joint doit appartenir à l'un des projets liés à la conversation."})

    def save(self, *args, **kwargs) -> None:
        if self.uploaded_file:
            self.original_filename = self.original_filename or Path(self.uploaded_file.name).name
            self.file_size = self.file_size if self.file_size is not None else self.uploaded_file.size
        self.original_filename = (self.original_filename or "").strip()
        self.mime_type = (self.mime_type or "").strip().lower()
        super().save(*args, **kwargs)
