

from __future__ import annotations

from uuid import uuid4

from django.db import models

from apps.companies.models import Company
from common.models import TimeStampedModel


class ClientEnvironment(TimeStampedModel):
    """
    Environnement client Easy Projet.

    Il est créé automatiquement lors de l'attribution de la première
    licence à une société. Il ne possède pas d'interface dédiée.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    company = models.OneToOneField(
        Company,
        on_delete=models.PROTECT,
        related_name="client_environment",
        verbose_name="Société cliente",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    class Meta:
        db_table = "client_environment"
        ordering = ["company__name"]
        verbose_name = "Environnement client"
        verbose_name_plural = "Environnements clients"

    def __str__(self) -> str:
        return self.company.name
