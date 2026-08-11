

from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalogs.models import CatalogValue
from apps.core.models import ClientEnvironment
from common.constants.integration import (
    INTEGRATION_CODE_LENGTH,
    INTEGRATION_CREDENTIAL_REFERENCE_LENGTH,
    INTEGRATION_NAME_LENGTH,
)
from common.models import TimeStampedModel
from common.services.code_generator import normalize_code_part


class ExternalIntegration(TimeStampedModel):
    """
    Service externe configuré pour un environnement client.

    Cette entité décrit ce qui est utilisable par Easy Projet.
    Les secrets techniques ne sont pas stockés directement ici.
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

    client_environment = models.ForeignKey(
        ClientEnvironment,
        on_delete=models.CASCADE,
        related_name="external_integrations",
        verbose_name="Environnement client",
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    service_type = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="integration_service_types",
        verbose_name="Type de service",
    )

    provider = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="integration_providers",
        verbose_name="Fournisseur",
    )

    connection_status = models.ForeignKey(
        CatalogValue,
        on_delete=models.PROTECT,
        related_name="integration_connection_statuses",
        verbose_name="État de connexion",
    )

    # ------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------

    code = models.CharField(
        max_length=INTEGRATION_CODE_LENGTH,
        verbose_name="Code",
    )

    name = models.CharField(
        max_length=INTEGRATION_NAME_LENGTH,
        verbose_name="Nom",
    )

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    priority = models.PositiveIntegerField(
        default=100,
        validators=[
            MinValueValidator(1),
        ],
        verbose_name="Priorité",
        help_text=(
            "Plus la valeur est faible, plus l'intégration "
            "est prioritaire."
        ),
    )

    # ------------------------------------------------------------------
    # Configuration technique
    # ------------------------------------------------------------------

    configuration = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Configuration",
        help_text=(
            "Paramètres techniques non sensibles du connecteur."
        ),
    )

    credential_reference = models.CharField(
        max_length=INTEGRATION_CREDENTIAL_REFERENCE_LENGTH,
        blank=True,
        verbose_name="Référence des credentials",
        help_text=(
            "Référence vers un stockage sécurisé de credentials. "
            "Aucun secret ne doit être stocké directement ici."
        ),
    )

    # ------------------------------------------------------------------
    # État
    # ------------------------------------------------------------------

    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
    )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def clean(self) -> None:
        super().clean()

        if (
            self.service_type_id
            and self.provider_id
            and self.service_type.catalog_type.code
            != "INTEGRATION_SERVICE_TYPE"
        ):
            raise ValidationError(
                {
                    "service_type": (
                        "La valeur sélectionnée n'appartient pas "
                        "au catalogue INTEGRATION_SERVICE_TYPE."
                    ),
                }
            )

        if (
            self.provider_id
            and self.provider.catalog_type.code
            != "INTEGRATION_PROVIDER"
        ):
            raise ValidationError(
                {
                    "provider": (
                        "La valeur sélectionnée n'appartient pas "
                        "au catalogue INTEGRATION_PROVIDER."
                    ),
                }
            )

        if (
            self.connection_status_id
            and self.connection_status.catalog_type.code
            != "INTEGRATION_CONNECTION_STATUS"
        ):
            raise ValidationError(
                {
                    "connection_status": (
                        "La valeur sélectionnée n'appartient pas "
                        "au catalogue "
                        "INTEGRATION_CONNECTION_STATUS."
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Persistance
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        self.code = normalize_code_part(
            self.code
        )

        self.name = self.name.strip()
        self.credential_reference = (
            self.credential_reference.strip()
        )

        super().save(*args, **kwargs)

    class Meta:
        db_table = "external_integration"
        ordering = [
            "client_environment",
            "service_type",
            "priority",
            "name",
        ]
        verbose_name = "Intégration externe"
        verbose_name_plural = "Intégrations externes"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "client_environment",
                    "code",
                ],
                name=(
                    "uniq_external_integration_code_"
                    "by_client_environment"
                ),
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.client_environment} - "
            f"{self.name}"
        )