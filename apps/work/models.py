

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.work_package import (
    WORK_PACKAGE_CODE_LENGTH,
    WORK_PACKAGE_DEFAULT_WORKLOAD_HOURS,
    WORK_PACKAGE_DESCRIPTION_LENGTH,
    WORK_PACKAGE_NAME_LENGTH,
)
from common.models import TimeStampedModel
from common.services.code_generator import (
    generate_scoped_code,
    normalize_code_part,
)


class WorkPackage(TimeStampedModel):
    """
    Lot de travaux rattaché à un projet.

    Le lot constitue une unité stable de pilotage et de communication.
    Les tâches portent l'organisation opérationnelle quotidienne.

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

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="work_packages",
        verbose_name="Projet",
    )

    # ------------------------------------------------------------------
    # Pilotage
    # ------------------------------------------------------------------

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="work_package_statuses",
        verbose_name="Statut",
    )

    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="managed_work_packages",
        null=True,
        blank=True,
        verbose_name="Responsable",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    code = models.CharField(
        max_length=WORK_PACKAGE_CODE_LENGTH,
        blank=True,
        verbose_name="Code",
    )

    name = models.CharField(
        max_length=WORK_PACKAGE_NAME_LENGTH,
        verbose_name="Nom",
    )

    description = models.TextField(
        max_length=WORK_PACKAGE_DESCRIPTION_LENGTH,
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
        default=WORK_PACKAGE_DEFAULT_WORKLOAD_HOURS,
        verbose_name="Charge planifiée (h)",
    )

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        verbose_name="Lot actif",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie la cohérence intrinsèque des dates du lot.

        La validation des impacts éventuels sur les dates du projet
        sera prise en charge par le mécanisme de propagation du
        planning, avec accord explicite de l'utilisateur.
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

        if self.project_id is None:
            raise ValueError(
                "Le projet doit être renseigné avant la génération "
                "du code du lot de travaux."
            )

        with transaction.atomic():
            project = (
                Project.objects
                .select_for_update()
                .get(pk=self.project_id)
            )

            self.code = generate_scoped_code(
                model=WorkPackage,
                parent=project,
                parent_field_name="project",
                prefix="LOT",
                max_length=WORK_PACKAGE_CODE_LENGTH,
            )

            super().save(*args, **kwargs)

    class Meta:
        db_table = "work_package"
        ordering = [
            "project",
            "code",
            "name",
        ]
        verbose_name = "Lot de travaux"
        verbose_name_plural = "Lots de travaux"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "code",
                ],
                name="uniq_work_package_code_by_project",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"