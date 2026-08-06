

from __future__ import annotations

import re
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models, transaction

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.risk import (
    RISK_DESCRIPTION_LENGTH,
    RISK_ESTIMATED_COST_DECIMAL_PLACES,
    RISK_ESTIMATED_COST_MAX_DIGITS,
    RISK_PLANNED_ACTIONS_LENGTH,
    RISK_REFERENCE_LENGTH,
    RISK_REFERENCE_PREFIX,
    RISK_REFERENCE_SEQUENCE_DIGITS,
    RISK_TITLE_LENGTH,
)
from common.models import TimeStampedModel
from common.services.code_generator import normalize_code_part


class Risk(TimeStampedModel):
    """
    Risque ou opportunité rattaché à un projet.

    La criticité et les informations de pilotage sont renseignées par
    l'utilisateur. Le modèle ne prend aucune décision automatique.
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
        related_name="risks",
        verbose_name="Projet",
    )

    # ------------------------------------------------------------------
    # Pilotage
    # ------------------------------------------------------------------

    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="owned_risks",
        null=True,
        blank=True,
        verbose_name="Pilote",
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    origin = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_origins",
        verbose_name="Origine",
    )

    risk_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_types",
        verbose_name="Type",
    )

    risk_class = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_classes",
        verbose_name="Classe",
    )

    impact = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_impacts",
        verbose_name="Impact",
    )

    severity = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_severities",
        verbose_name="Gravité",
    )

    probability = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_probabilities",
        verbose_name="Probabilité",
    )

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_statuses",
        verbose_name="État",
    )

    criticality = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_criticalities",
        verbose_name="Criticité",
    )

    review_frequency = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="risk_review_frequencies",
        null=True,
        blank=True,
        verbose_name="Fréquence de revue",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    reference = models.CharField(
        max_length=RISK_REFERENCE_LENGTH,
        blank=True,
        verbose_name="Référence",
    )

    title = models.CharField(
        max_length=RISK_TITLE_LENGTH,
        verbose_name="Titre",
    )

    description = models.TextField(
        max_length=RISK_DESCRIPTION_LENGTH,
        blank=True,
        verbose_name="Description",
    )

    # ------------------------------------------------------------------
    # Évaluation
    # ------------------------------------------------------------------

    occurrence_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'apparition",
    )

    closure_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de clôture",
    )

    estimated_cost = models.DecimalField(
        max_digits=RISK_ESTIMATED_COST_MAX_DIGITS,
        decimal_places=RISK_ESTIMATED_COST_DECIMAL_PLACES,
        null=True,
        blank=True,
        verbose_name="Coût estimé",
    )

    last_review_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date de la dernière revue",
    )

    planned_actions = models.TextField(
        max_length=RISK_PLANNED_ACTIONS_LENGTH,
        blank=True,
        verbose_name="Actions prévues",
    )

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        verbose_name="Risque actif",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Vérifie uniquement la cohérence propre au risque.
        """
        super().clean()

        if (
            self.occurrence_date is not None
            and self.closure_date is not None
            and self.closure_date < self.occurrence_date
        ):
            raise ValidationError(
                {
                    "closure_date": (
                        "La date de clôture ne peut pas être "
                        "antérieure à la date d'apparition."
                    ),
                }
            )

        if (
            self.estimated_cost is not None
            and self.estimated_cost < 0
        ):
            raise ValidationError(
                {
                    "estimated_cost": (
                        "Le coût estimé doit être positif ou nul."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        """
        Normalise ou génère la référence avant l'enregistrement.
        """
        self.title = self.title.strip()

        if self.reference:
            self.reference = normalize_code_part(
                self.reference
            )

            super().save(*args, **kwargs)
            return

        if self.project_id is None:
            raise ValueError(
                "Le projet doit être renseigné avant la génération "
                "de la référence du risque."
            )

        with transaction.atomic():
            Project.objects.select_for_update().get(
                pk=self.project_id
            )

            self.reference = self._generate_reference()

            super().save(*args, **kwargs)

    def _generate_reference(self) -> str:
        """
        Génère la prochaine référence séquentielle du projet.

        Exemple : RSK_001, RSK_002, RSK_003.
        """
        normalized_prefix = normalize_code_part(
            RISK_REFERENCE_PREFIX
        )

        expression = re.compile(
            rf"^{re.escape(normalized_prefix)}_(\d+)$"
        )

        existing_references = (
            Risk.objects
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
            f"{next_number:0{RISK_REFERENCE_SEQUENCE_DIGITS}d}"
        )

        if len(reference) > RISK_REFERENCE_LENGTH:
            raise ValueError(
                "La référence générée dépasse la longueur maximale "
                f"de {RISK_REFERENCE_LENGTH} caractères."
            )

        return reference

    class Meta:
        db_table = "risk"
        ordering = [
            "project",
            "reference",
            "title",
        ]
        verbose_name = "Risque"
        verbose_name_plural = "Risques"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "project",
                    "reference",
                ],
                name="uniq_risk_reference_by_project",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.reference} - {self.title}"