

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.catalogs.models import CatalogValue
from apps.users.models import User
from apps.work.models import WorkPackage
from common.constants.task import (
    TASK_CODE_LENGTH,
    TASK_DEFAULT_PLANNED_WORKLOAD_HOURS,
    TASK_DEFAULT_PROGRESS_PERCENT,
    TASK_DEFAULT_REMAINING_WORKLOAD_HOURS,
    TASK_DESCRIPTION_LENGTH,
    TASK_MAX_PROGRESS_PERCENT,
    TASK_MIN_PROGRESS_PERCENT,
    TASK_NAME_LENGTH,
)
from common.models import TimeStampedModel
from common.services.code_generator import (
    generate_scoped_code,
    normalize_code_part,
)


class Task(TimeStampedModel):
    """
    Tâche opérationnelle d'un lot de travaux.

    La tâche constitue le niveau de pilotage quotidien.

    Les dates initiales constituent la référence de planification.
    Les dates courantes représentent le planning actuellement validé.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # Rattachement
    # ------------------------------------------------------------------

    work_package = models.ForeignKey(
        WorkPackage,
        on_delete=models.PROTECT,
        related_name="tasks",
        verbose_name="Lot de travaux",
    )

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="task_statuses",
        verbose_name="Statut",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    code = models.CharField(
        max_length=TASK_CODE_LENGTH,
        blank=True,
        verbose_name="Code",
    )

    name = models.CharField(
        max_length=TASK_NAME_LENGTH,
        verbose_name="Nom",
    )

    description = models.TextField(
        max_length=TASK_DESCRIPTION_LENGTH,
        blank=True,
        verbose_name="Description",
    )

    # ------------------------------------------------------------------
    # Planning - dates initiales
    # ------------------------------------------------------------------

    initial_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Début initial",
    )

    initial_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin initiale",
    )

    # ------------------------------------------------------------------
    # Planning - dates courantes
    # ------------------------------------------------------------------

    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Début",
    )

    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fin",
    )

    planned_workload_hours = models.PositiveIntegerField(
        default=TASK_DEFAULT_PLANNED_WORKLOAD_HOURS,
        verbose_name="Charge planifiée (h)",
    )

    remaining_workload_hours = models.PositiveIntegerField(
        default=TASK_DEFAULT_REMAINING_WORKLOAD_HOURS,
        verbose_name="Reste à faire (h)",
    )

    progress_percent = models.PositiveSmallIntegerField(
        default=TASK_DEFAULT_PROGRESS_PERCENT,
        verbose_name="Avancement (%)",
    )

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        verbose_name="Tâche active",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie la cohérence intrinsèque de la tâche.

        Les éventuels impacts des dates de la tâche sur les dates
        du lot de travaux seront traités par le mécanisme de
        propagation du planning, après validation de l'utilisateur.
        """
        super().clean()

        if (
            self.initial_start_date is not None
            and self.initial_end_date is not None
            and self.initial_end_date < self.initial_start_date
        ):
            raise ValidationError(
                {
                    "initial_end_date": (
                        "La fin initiale ne peut pas être antérieure "
                        "au début initial."
                    ),
                }
            )

        if (
            self.start_date is not None
            and self.end_date is not None
            and self.end_date < self.start_date
        ):
            raise ValidationError(
                {
                    "end_date": (
                        "La date de fin ne peut pas être antérieure "
                        "à la date de début."
                    ),
                }
            )

        if not (
            TASK_MIN_PROGRESS_PERCENT
            <= self.progress_percent
            <= TASK_MAX_PROGRESS_PERCENT
        ):
            raise ValidationError(
                {
                    "progress_percent": (
                        "Le pourcentage d'avancement doit être "
                        f"compris entre {TASK_MIN_PROGRESS_PERCENT} "
                        f"et {TASK_MAX_PROGRESS_PERCENT}."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        """
        Normalise ou génère le code avant l'enregistrement.

        Lorsqu'une date courante n'est pas renseignée, elle est
        initialisée avec la date initiale correspondante.
        """
        self.name = self.name.strip()

        initialized_fields = set()

        if (
            self.start_date is None
            and self.initial_start_date is not None
        ):
            self.start_date = self.initial_start_date
            initialized_fields.add("start_date")

        if (
            self.end_date is None
            and self.initial_end_date is not None
        ):
            self.end_date = self.initial_end_date
            initialized_fields.add("end_date")

        update_fields = kwargs.get("update_fields")

        if (
            update_fields is not None
            and initialized_fields
        ):
            update_fields = set(update_fields)
            update_fields.update(initialized_fields)
            kwargs["update_fields"] = update_fields

        if self.code:
            self.code = normalize_code_part(self.code)
            super().save(*args, **kwargs)
            return

        if self.work_package_id is None:
            raise ValueError(
                "Le lot de travaux doit être renseigné avant "
                "la génération du code de la tâche."
            )

        with transaction.atomic():
            work_package = (
                WorkPackage.objects
                .select_for_update()
                .get(pk=self.work_package_id)
            )

            self.code = generate_scoped_code(
                model=Task,
                parent=work_package,
                parent_field_name="work_package",
                prefix=f"TSK_{work_package.code}",
                max_length=TASK_CODE_LENGTH,
            )

            super().save(*args, **kwargs)

    class Meta:
        db_table = "task"
        ordering = [
            "work_package",
            "code",
            "name",
        ]
        verbose_name = "Tâche"
        verbose_name_plural = "Tâches"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "work_package",
                    "code",
                ],
                name="uniq_task_code_by_work_package",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class TaskAssignment(TimeStampedModel):
    """
    Affectation individuelle d'un utilisateur à une tâche.

    L'affectation est indépendante de toute notion d'équipe.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="assignments",
        verbose_name="Tâche",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="task_assignments",
        verbose_name="Utilisateur",
    )

    role = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="task_assignment_roles",
        verbose_name="Rôle sur la tâche",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Affectation active",
    )

    class Meta:
        db_table = "task_assignment"
        ordering = [
            "task",
            "user__last_name",
            "user__first_name",
        ]
        verbose_name = "Affectation à une tâche"
        verbose_name_plural = "Affectations aux tâches"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "task",
                    "user",
                ],
                name="uniq_task_assignment_user",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.task.code} - "
            f"{self.user.last_name} "
            f"{self.user.first_name}"
        )