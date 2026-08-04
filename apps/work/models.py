

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

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


class WorkPackage(TimeStampedModel):
    """
    Lot de travaux rattaché à un projet.

    Le lot constitue une unité stable de pilotage et de communication.
    Les tâches portent l'organisation opérationnelle quotidienne.
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
    # Planning
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

    def clean(self) -> None:
        """
        Vérifie uniquement la cohérence propre au lot.

        Aucune date de projet, de tâche ou de rapport d'activité
        n'est recalculée automatiquement.
        """
        super().clean()

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

    def save(self, *args, **kwargs) -> None:
        self.code = self.code.strip().upper()
        self.name = self.name.strip()

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