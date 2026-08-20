

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.catalogs.models import CatalogValue
from apps.users.models import User
from apps.work.models import WorkPackage
from common.constants.task import (
    TASK_ASSIGNMENT_DEFAULT_ALLOCATION_PERCENT,
    TASK_ASSIGNMENT_MAX_ALLOCATION_PERCENT,
    TASK_ASSIGNMENT_MIN_ALLOCATION_PERCENT,
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

    Le taux de charge représente la part de capacité de la ressource
    affectée à la tâche pendant sa période de planification.
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

    allocation_percent = models.PositiveSmallIntegerField(
        default=TASK_ASSIGNMENT_DEFAULT_ALLOCATION_PERCENT,
        verbose_name="Taux de charge (%)",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Affectation active",
    )

    def clean(self) -> None:
        """
        Vérifie la cohérence de l'affectation.
        """
        super().clean()

        if not (
            TASK_ASSIGNMENT_MIN_ALLOCATION_PERCENT
            <= self.allocation_percent
            <= TASK_ASSIGNMENT_MAX_ALLOCATION_PERCENT
        ):
            raise ValidationError(
                {
                    "allocation_percent": (
                        "Le taux de charge doit être compris entre "
                        f"{TASK_ASSIGNMENT_MIN_ALLOCATION_PERCENT} "
                        "et "
                        f"{TASK_ASSIGNMENT_MAX_ALLOCATION_PERCENT} %."
                    ),
                }
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


class TaskDependency(TimeStampedModel):
    """
    Dépendance d'ordonnancement entre deux tâches.

    Une dépendance relie une tâche antécédente à une tâche
    successeure.

    Types supportés :
    - FS : Fin -> Début ;
    - SS : Début -> Début ;
    - FF : Fin -> Fin ;
    - SF : Début -> Fin.

    Le décalage est exprimé en jours calendaires.

    Un décalage positif crée une attente.
    Un décalage négatif autorise un chevauchement.
    """

    class DependencyType(models.TextChoices):
        FINISH_TO_START = (
            "FS",
            "Fin → Début",
        )
        START_TO_START = (
            "SS",
            "Début → Début",
        )
        FINISH_TO_FINISH = (
            "FF",
            "Fin → Fin",
        )
        START_TO_FINISH = (
            "SF",
            "Début → Fin",
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    predecessor = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="successor_dependencies",
        verbose_name="Tâche antécédente",
    )

    successor = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="predecessor_dependencies",
        verbose_name="Tâche successeure",
    )

    dependency_type = models.CharField(
        max_length=2,
        choices=DependencyType.choices,
        default=DependencyType.FINISH_TO_START,
        verbose_name="Type de dépendance",
    )

    lag_days = models.IntegerField(
        default=0,
        verbose_name="Décalage (jours)",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Dépendance active",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie la cohérence métier de la dépendance.

        Règles :
        - une tâche ne peut pas dépendre d'elle-même ;
        - les deux tâches doivent appartenir au même projet ;
        - une dépendance active ne doit pas créer de cycle.
        """
        super().clean()

        if (
            self.predecessor_id is None
            or self.successor_id is None
        ):
            return

        if self.predecessor_id == self.successor_id:
            raise ValidationError(
                {
                    "predecessor": (
                        "Une tâche ne peut pas dépendre "
                        "d'elle-même."
                    ),
                }
            )

        predecessor_project_id = (
            self.predecessor
            .work_package
            .project_id
        )

        successor_project_id = (
            self.successor
            .work_package
            .project_id
        )

        if (
            predecessor_project_id
            != successor_project_id
        ):
            raise ValidationError(
                {
                    "predecessor": (
                        "Les tâches d'une dépendance doivent "
                        "appartenir au même projet."
                    ),
                }
            )

        if (
            self.is_active
            and self._would_create_cycle()
        ):
            raise ValidationError(
                {
                    "predecessor": (
                        "Cette dépendance créerait une boucle "
                        "dans l'enchaînement des tâches."
                    ),
                }
            )
    
    def _would_create_cycle(
        self,
    ) -> bool:
        """
        Indique si la dépendance courante créerait un cycle.

        Pour ajouter :

            predecessor -> successor

        il ne doit pas déjà exister de chemin actif :

            successor -> ... -> predecessor
        """

        dependencies = (
            TaskDependency.objects
            .filter(is_active=True)
        )

        if self.pk:
            dependencies = dependencies.exclude(
                pk=self.pk
            )

        adjacency: dict[
            object,
            set,
        ] = {}

        for (
            predecessor_id,
            successor_id,
        ) in dependencies.values_list(
            "predecessor_id",
            "successor_id",
        ):
            adjacency.setdefault(
                predecessor_id,
                set(),
            ).add(
                successor_id
            )

        target_id = self.predecessor_id

        pending = [
            self.successor_id
        ]

        visited = set()

        while pending:
            task_id = pending.pop()

            if task_id == target_id:
                return True

            if task_id in visited:
                continue

            visited.add(
                task_id
            )

            pending.extend(
                adjacency.get(
                    task_id,
                    ()
                )
            )

        return False

    class Meta:
        db_table = "task_dependency"

        ordering = [
            "predecessor__work_package",
            "predecessor__code",
            "successor__code",
        ]

        verbose_name = "Dépendance de tâche"
        verbose_name_plural = "Dépendances de tâches"

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "predecessor",
                    "successor",
                ],
                name=(
                    "uniq_task_dependency_"
                    "predecessor_successor"
                ),
            ),
            models.CheckConstraint(
                condition=~models.Q(
                    predecessor=models.F(
                        "successor"
                    )
                ),
                name=(
                    "task_dependency_"
                    "predecessor_not_successor"
                ),
            ),
        ]

    def __str__(self) -> str:
        lag = ""

        if self.lag_days > 0:
            lag = f" +{self.lag_days} j"

        elif self.lag_days < 0:
            lag = f" {self.lag_days} j"

        return (
            f"{self.predecessor.code} "
            f"→ "
            f"{self.successor.code} "
            f"({self.dependency_type}{lag})"
        )