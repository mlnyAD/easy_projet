

# apps/todos/models.py

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.users.models import User
from common.models import TimeStampedModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from apps.projects.models import Project


class TodoAction(TimeStampedModel):
    """
    Action personnelle ou assignée à un ou plusieurs utilisateurs.

    Une action peut être associée à un objet métier, mais elle n'est
    jamais générée automatiquement par cet objet.
    """

    class Origin(models.TextChoices):
        PERSONAL = (
            "PERSONAL",
            "Personnelle",
        )
        ASSIGNED = (
            "ASSIGNED",
            "Assignée",
        )

    class Status(models.TextChoices):
        TODO = (
            "TODO",
            "À faire",
        )
        IN_PROGRESS = (
            "IN_PROGRESS",
            "En cours",
        )
        SUSPENDED = (
            "SUSPENDED",
            "Suspendue",
        )
        COMPLETED = (
            "COMPLETED",
            "Terminée",
        )
        ABANDONED = (
            "ABANDONED",
            "Abandonnée",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="owned_todo_actions",
        verbose_name="Rédacteur",
    )

    origin = models.CharField(
        max_length=20,
        choices=Origin.choices,
        default=Origin.PERSONAL,
        verbose_name="Origine",
    )

    title = models.CharField(
        max_length=150,
        verbose_name="Titre",
    )

    details = models.TextField(
        blank=True,
        verbose_name="Détails",
    )

    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de fin",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        verbose_name="État",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Date de réalisation",
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="todo_actions",
        null=True,
        blank=True,
        verbose_name="Projet associé",
    )

    context_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="Type d'objet associé",
    )

    context_object_id = models.UUIDField(
        null=True,
        blank=True,
        verbose_name="Objet associé",
    )

    context_object = GenericForeignKey(
        "context_content_type",
        "context_object_id",
    )    

    def clean(self) -> None:
        super().clean()

        has_content_type = (
            self.context_content_type_id is not None
        )

        has_object_id = (
            self.context_object_id is not None
        )

        if has_content_type != has_object_id:
            raise ValidationError(
                {
                    "context_object_id": (
                        "Le type et l'objet associés doivent "
                        "être renseignés ensemble."
                    ),
                }
            )

        if (
            self.context_content_type_id is not None
            and self.context_object is None
        ):
            raise ValidationError(
                {
                    "context_object_id": (
                        "L'objet métier associé est introuvable."
                    ),
                }
            )
            
    def save(self, *args, **kwargs) -> None:
        self.title = self.title.strip()

        if self.status == self.Status.COMPLETED:
            if self.completed_at is None:
                self.completed_at = timezone.now()
        else:
            self.completed_at = None

        super().save(*args, **kwargs)
    

    class Meta:
        db_table = "todo_action"
        ordering = [
            "status",
            "due_date",
            "created_at",
        ]
        verbose_name = "Action Todo"
        verbose_name_plural = "Actions Todo"

    def __str__(self) -> str:
        return self.title


class TodoActionRecipient(TimeStampedModel):
    """
    Destinataire d'une action assignée.
    """

    class Role(models.TextChoices):
        ACTION = (
            "ACTION",
            "Pour action",
        )
        INFORMATION = (
            "INFORMATION",
            "Pour information",
        )
        COLLABORATION = (
            "COLLABORATION",
            "Action commune",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    action = models.ForeignKey(
        TodoAction,
        on_delete=models.CASCADE,
        related_name="recipients",
        verbose_name="Action",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="todo_actions_received",
        verbose_name="Destinataire",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        verbose_name="Rôle",
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="Date de lecture",
    )
    
    def clean(self) -> None:
        super().clean()

        if self.action.origin == TodoAction.Origin.PERSONAL:
            raise ValidationError(
                {
                    "action": (
                        "Une action personnelle ne peut pas "
                        "avoir de destinataire."
                    ),
                }
            )

    class Meta:
        db_table = "todo_action_recipient"
        ordering = [
            "action",
            "user__last_name",
            "user__first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "action",
                    "user",
                ],
                name="uniq_todo_action_recipient",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.action.title} - "
            f"{self.user}"
        )