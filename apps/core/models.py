

from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.catalogs.models import CatalogValue
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


class ClientEnvironmentMembership(TimeStampedModel):
    """
    Rattachement d'un utilisateur à un environnement client.

    Cette relation indique que l'utilisateur est connu
    et autorisé dans cet environnement client.

    Un administrateur client peut être titulaire ou délégué.
    Titulaire et délégués disposent des mêmes droits.
    Au maximum un administrateur client actif peut être titulaire
    dans un environnement client.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    client_environment = models.ForeignKey(
        ClientEnvironment,
        on_delete=models.CASCADE,
        related_name="user_memberships",
        verbose_name="Environnement client",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="client_environment_memberships",
        verbose_name="Utilisateur",
    )

    employment_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="client_environment_memberships",
        null=True,
        blank=True,
        verbose_name="Type d'emploi",
    )

    is_client_admin = models.BooleanField(
        default=False,
        verbose_name="Administrateur client",
    )

    is_client_admin_responsible = models.BooleanField(
        default=False,
        verbose_name="Administrateur client titulaire",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    class Meta:
        db_table = "client_environment_membership"
        ordering = [
            "client_environment",
            "user__last_name",
            "user__first_name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "client_environment",
                    "user",
                ],
                name=(
                    "uq_client_environment_membership_"
                    "environment_user"
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "client_environment",
                ],
                condition=Q(
                    is_client_admin_responsible=True,
                    is_active=True,
                ),
                name=(
                    "uq_client_environment_membership_"
                    "active_responsible"
                ),
            ),
        ]
        verbose_name = "Rattachement utilisateur à un environnement client"
        verbose_name_plural = (
            "Rattachements utilisateurs aux environnements clients"
        )

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.employment_type_id
            and self.employment_type.catalog_type.code
            != "USER_EMPLOYMENT_TYPE"
        ):
            errors["employment_type"] = (
                "Le type d'emploi doit appartenir au catalogue "
                "USER_EMPLOYMENT_TYPE."
            )

        if (
            self.is_client_admin_responsible
            and not self.is_client_admin
        ):
            errors["is_client_admin_responsible"] = (
                "L'administrateur client titulaire doit être "
                "administrateur client."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return (
            f"{self.client_environment} - "
            f"{self.user}"
        )