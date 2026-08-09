

from __future__ import annotations

import re
from decimal import Decimal
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models, transaction

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.meeting import (
    MEETING_COMMENTS_LENGTH,
    MEETING_DURATION_DECIMAL_PLACES,
    MEETING_DURATION_MAX_DIGITS,
    MEETING_DURATION_MAX_HOURS,
    MEETING_LOCATION_LENGTH,
    MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH,
    MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH,
    MEETING_REFERENCE_LENGTH,
    MEETING_REFERENCE_PREFIX,
    MEETING_REFERENCE_SEQUENCE_DIGITS,
    MEETING_SUBJECT_LENGTH,
)
from common.models import TimeStampedModel
from common.services.code_generator import normalize_code_part


class Meeting(TimeStampedModel):
    """
    Réunion organisée dans le cadre d'un projet.

    Les notes sont destinées aux participants.
    Les commentaires restent réservés à un usage interne.
    """

    # ------------------------------------------------------------------
    # Identifiant
    # ------------------------------------------------------------------

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # Rattachement
    # ------------------------------------------------------------------

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="meetings",
        verbose_name="Projet",
    )

    # ------------------------------------------------------------------
    # Pilotage
    # ------------------------------------------------------------------

    organizer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="organized_meetings",
        verbose_name="Organisateur",
    )

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="meeting_statuses",
        verbose_name="État",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    reference = models.CharField(
        max_length=MEETING_REFERENCE_LENGTH,
        blank=True,
        verbose_name="Référence",
    )

    subject = models.CharField(
        max_length=MEETING_SUBJECT_LENGTH,
        verbose_name="Objet",
    )

    # ------------------------------------------------------------------
    # Organisation
    # ------------------------------------------------------------------

    scheduled_at = models.DateTimeField(
        verbose_name="Date et heure",
    )

    duration_hours = models.DecimalField(
        max_digits=MEETING_DURATION_MAX_DIGITS,
        decimal_places=MEETING_DURATION_DECIMAL_PLACES,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(
                Decimal(str(MEETING_DURATION_MAX_HOURS))
            ),
        ],
        verbose_name="Durée (h)",
    )

    location = models.CharField(
        max_length=MEETING_LOCATION_LENGTH,
        blank=True,
        verbose_name="Lieu",
    )

    # ------------------------------------------------------------------
    # Ordre du jour
    # ------------------------------------------------------------------

    agenda = models.TextField(
        max_length=MEETING_COMMENTS_LENGTH,
        blank=True,
        verbose_name="Ordre du jour",
    )

    # ------------------------------------------------------------------
    # Informations
    # ------------------------------------------------------------------

    notes = models.TextField(
        max_length=MEETING_COMMENTS_LENGTH,
        blank=True,
        verbose_name="Notes de convocation",
        help_text=(
            "Informations transmises aux participants "
            "avec l'invitation."
        ),
    )

    comments = models.TextField(
        max_length=MEETING_COMMENTS_LENGTH,
        blank=True,
        verbose_name="Commentaires internes",
        help_text=(
            "Informations internes non transmises "
            "aux participants."
        ),
    )

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        verbose_name="Réunion active",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        super().clean()

        if (
            self.duration_hours is not None
            and self.duration_hours <= 0
        ):
            raise ValidationError(
                {
                    "duration_hours": (
                        "La durée doit être strictement positive."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        self.subject = self.subject.strip()
        self.location = self.location.strip()
        self.agenda = self.agenda.strip()
        self.notes = self.notes.strip()
        self.comments = self.comments.strip()

        if self.reference:
            self.reference = normalize_code_part(
                self.reference
            )

            super().save(*args, **kwargs)
            return

        if self.project_id is None:
            raise ValueError(
                "Le projet doit être renseigné avant la génération "
                "de la référence de la réunion."
            )

        with transaction.atomic():
            Project.objects.select_for_update().get(
                pk=self.project_id
            )

            self.reference = self._generate_reference()

            super().save(*args, **kwargs)

    def _generate_reference(self) -> str:
        normalized_prefix = normalize_code_part(
            MEETING_REFERENCE_PREFIX
        )

        expression = re.compile(
            rf"^{re.escape(normalized_prefix)}_(\d+)$"
        )

        existing_references = (
            Meeting.objects
            .filter(
                project_id=self.project_id,
                reference__startswith=(
                    f"{normalized_prefix}_"
                ),
            )
            .values_list(
                "reference",
                flat=True,
            )
        )

        highest_number = 0

        for existing_reference in existing_references:
            match = expression.match(existing_reference)

            if match is not None:
                highest_number = max(
                    highest_number,
                    int(match.group(1)),
                )

        next_number = highest_number + 1

        reference = (
            f"{normalized_prefix}_"
            f"{next_number:0{MEETING_REFERENCE_SEQUENCE_DIGITS}d}"
        )

        if len(reference) > MEETING_REFERENCE_LENGTH:
            raise ValueError(
                "La référence générée dépasse la longueur "
                f"maximale de {MEETING_REFERENCE_LENGTH} caractères."
            )

        return reference

    class Meta:
        db_table = "meeting"
        ordering = [
            "project",
            "-scheduled_at",
            "reference",
        ]
        verbose_name = "Réunion"
        verbose_name_plural = "Réunions"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "reference",
                ],
                name="uniq_meeting_reference_by_project",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reference} - {self.subject}"


class MeetingParticipant(TimeStampedModel):
    """
    Participant interne ou externe invité à une réunion.
    """

    # ------------------------------------------------------------------
    # Identifiant
    # ------------------------------------------------------------------

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # Rattachement
    # ------------------------------------------------------------------

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="participants",
        verbose_name="Réunion",
    )

    # ------------------------------------------------------------------
    # Participant
    # ------------------------------------------------------------------

    participant = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="meeting_participations",
        null=True,
        blank=True,
        verbose_name="Participant interne",
    )

    external_name = models.CharField(
        max_length=MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH,
        blank=True,
        verbose_name="Nom du participant externe",
    )

    external_email = models.EmailField(
        max_length=MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH,
        blank=True,
        verbose_name="Email du participant externe",
    )

    # ------------------------------------------------------------------
    # Invitation
    # ------------------------------------------------------------------

    invitation_response = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="meeting_invitation_responses",
        null=True,
        blank=True,
        verbose_name="Réponse à l'invitation",
    )

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        verbose_name="Participation active",
    )

    # ------------------------------------------------------------------
    # Propriétés
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        if self.participant_id is not None:
            return str(self.participant)

        if self.external_name:
            return self.external_name

        return self.external_email

    @property
    def is_external(self) -> bool:
        return self.participant_id is None

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        super().clean()

        external_name = self.external_name.strip()
        external_email = self.external_email.strip()

        has_internal_participant = (
            self.participant_id is not None
        )

        has_external_data = bool(
            external_name
            or external_email
        )

        if (
            has_internal_participant
            and has_external_data
        ):
            raise ValidationError(
                "Un participant ne peut pas être "
                "à la fois interne et externe."
            )

        if (
            not has_internal_participant
            and not external_name
            and not external_email
        ):
            raise ValidationError(
                {
                    "external_email": (
                        "Le nom ou l'adresse email du participant "
                        "externe est obligatoire."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        self.external_name = self.external_name.strip()
        self.external_email = (
            self.external_email.strip().lower()
        )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "meeting_participant"
        ordering = [
            "meeting",
            "participant",
            "external_name",
        ]
        verbose_name = "Participant à une réunion"
        verbose_name_plural = "Participants aux réunions"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "meeting",
                    "participant",
                ],
                condition=models.Q(
                    participant__isnull=False,
                ),
                name="uniq_internal_participant_by_meeting",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.meeting.reference} - "
            f"{self.display_name}"
        )