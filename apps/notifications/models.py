from __future__ import annotations

from uuid import uuid4

from django.db import models

from apps.projects.models import Project
from apps.users.models import User
from common.models import TimeStampedModel


class Notification(TimeStampedModel):
    """Alerte personnelle produite par une action applicative."""

    class Kind(models.TextChoices):
        MEETING_INVITATION = (
            "MEETING_INVITATION",
            "Invitation à une réunion",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Destinataire",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        verbose_name="Projet",
    )
    kind = models.CharField(
        max_length=40,
        choices=Kind.choices,
        verbose_name="Type",
    )
    source_key = models.CharField(
        max_length=255,
        verbose_name="Clé fonctionnelle",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Titre",
    )
    body = models.TextField(
        blank=True,
        max_length=1000,
        verbose_name="Détail",
    )
    target_url = models.CharField(
        max_length=500,
        verbose_name="Lien cible",
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Lu le",
    )

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=("user", "source_key"),
                name="uniq_notification_user_source_key",
            ),
        ]
        indexes = [
            models.Index(
                fields=("user", "read_at", "-created_at"),
                name="notification_user_read_idx",
            ),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def __str__(self) -> str:
        return self.title
