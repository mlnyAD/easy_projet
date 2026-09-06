

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.core.models import ClientEnvironment
from common.forms.fields import CatalogModelChoiceField

from .models import ExternalIntegration
from .services.access import IntegrationAccessService


class ExternalIntegrationForm(forms.ModelForm):
    """
    Formulaire de création et de modification
    d'une intégration externe.
    """

    service_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="INTEGRATION_SERVICE_TYPE",
        required=True,
        label="Type de service",
    )

    provider = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="INTEGRATION_PROVIDER",
        required=True,
        label="Fournisseur",
    )

    connection_status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="INTEGRATION_CONNECTION_STATUS",
        required=True,
        label="État de connexion",
    )

    class Meta:
        model = ExternalIntegration

        fields = (
            # Rattachement
            "client_environment",

            # Classification
            "service_type",
            "provider",
            "connection_status",

            # Identification
            "code",
            "name",

            # Orchestration
            "priority",

            # État
            "is_active",
        )

        labels = {
            "client_environment": "Environnement client",
            "code": "Code",
            "name": "Nom",
            "priority": "Priorité",
            "is_active": "Intégration active",
        }

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
            "priority": forms.NumberInput(
                attrs={
                    "min": 1,
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
        }

    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        if user is None:
            self.fields["client_environment"].queryset = (
                ClientEnvironment.objects.none()
            )
        else:
            self.fields["client_environment"].queryset = (
                IntegrationAccessService
                .get_assignable_environments(user)
            )

        catalog_fields = (
            (
                "service_type",
                "INTEGRATION_SERVICE_TYPE",
            ),
            (
                "provider",
                "INTEGRATION_PROVIDER",
            ),
            (
                "connection_status",
                "INTEGRATION_CONNECTION_STATUS",
            ),
        )

        for field_name, catalog_code in catalog_fields:
            self._configure_catalog_field(
                field_name=field_name,
                catalog_code=catalog_code,
            )

        if not self.is_bound and not self.instance.pk:
            for field_name, _ in catalog_fields:
                self._apply_catalog_default(field_name)

    def _configure_catalog_field(
        self,
        *,
        field_name: str,
        catalog_code: str,
    ) -> None:
        """
        Configure le queryset d'un champ catalogue.
        """
        field = self.fields[field_name]

        field.queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
                is_active=True,
            )
            .select_related("catalog_type")
            .order_by(
                "level",
                "sort_order",
                "label",
            )
        )

    def _apply_catalog_default(
        self,
        field_name: str,
    ) -> None:
        """
        Applique la valeur par défaut éventuelle
        du catalogue.
        """
        default_value = (
            self.fields[field_name]
            .queryset
            .filter(is_default=True)
            .first()
        )

        if default_value is not None:
            self.initial[field_name] = default_value.pk