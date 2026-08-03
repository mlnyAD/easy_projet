

from __future__ import annotations

from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models

from apps.catalogs.models import CatalogValue
from apps.core.models import ClientEnvironment
from common.constants.license import (
    DEFAULT_LICENSE_PROJECT_CAPACITY,
    LICENSE_REFERENCE_LENGTH,
    MIN_LICENSE_PROJECT_CAPACITY,
)
from common.models import TimeStampedModel


class License(TimeStampedModel):
    """
    Licence Easy Projet attribuée à un environnement client.

    Une licence possède une capacité maximale en nombre de projets.
    Le contrat actuel utilise une capacité égale à 1.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    client_environment = models.ForeignKey(
        ClientEnvironment,
        on_delete=models.PROTECT,
        related_name="licenses",
        verbose_name="Environnement client",
    )

    reference = models.CharField(
        max_length=LICENSE_REFERENCE_LENGTH,
        verbose_name="Référence commerciale",
        help_text=(
            "Numéro de commande client ou numéro de devis."
        ),
    )

    status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="licenses",
        verbose_name="Statut",
    )

    project_capacity = models.PositiveIntegerField(
        default=DEFAULT_LICENSE_PROJECT_CAPACITY,
        validators=[
            MinValueValidator(
                MIN_LICENSE_PROJECT_CAPACITY,
            ),
        ],
        verbose_name="Capacité en projets",
    )

    granted_at = models.DateField(
        verbose_name="Date d'attribution",
    )

    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration",
    )

    def save(self, *args, **kwargs):
        self.reference = self.reference.strip()

        super().save(*args, **kwargs)

    @property
    def company_name(self) -> str:
        return self.client_environment.company.name


    @property
    def status_label(self) -> str:
        return self.status.label

    class Meta:
        db_table = "license"
        ordering = [
            "-granted_at",
            "reference",
        ]
        verbose_name = "Licence"
        verbose_name_plural = "Licences"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "client_environment",
                    "reference",
                ],
                name="uniq_license_reference_by_environment",
            ),
        ]

    def __str__(self) -> str:
        return self.reference
