

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from apps.users.models import User
from common.constants.project import (
    PROJECT_ADDRESS_LENGTH,
    PROJECT_CITY_LENGTH,
    PROJECT_COMMENT_LENGTH,
    PROJECT_CONTRACT_REFERENCE_LENGTH,
    PROJECT_COUNTRY_LENGTH,
    PROJECT_CURRENCY_LENGTH,
    PROJECT_DESCRIPTION_LENGTH,
    PROJECT_NAME_LENGTH,
    PROJECT_POSTAL_CODE_LENGTH,
    PROJECT_REFERENCE_LENGTH,
)
from common.forms.fields import CatalogModelChoiceField

from .models import Project, ProjectMembership


class ProjectForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'un projet.
    """

    status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="PROJECT_STATUS",
        required=True,
        label="Statut",
    )

    project_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="PROJECT_TYPE",
        required=False,
        label="Type de projet",
    )

    class Meta:
        model = Project

        fields = (
            # Identification
            "reference",
            "name",
            "description",
            "company",
            "project_manager",
            "status",
            "is_active",

            # Client et contrat
            "owner_company",
            "designer_company",
            "project_type",
            "contract_reference",
            "comments",

            # Localisation
            "address_1",
            "address_2",
            "address_3",
            "postal_code",
            "city",
            "country",

            # Charge et planning
            "planned_workload_hours",
            "contractual_start_date",
            "contractual_end_date",
            "start_date_review",
            "end_date_review",
            "receipt_date_init",
            "receipt_date_review",
            "delivery_date_init",
            "delivery_date_review",

            # Données commerciales
            "amount_quote_ht",
            "amount_quote_ttc",
            "amount_order_ht",
            "amount_order_ttc",
            "currency",
            "budget_comments",
        )

        labels = {
            "is_active": "Projet actif",
        }

        widgets = {
            "reference": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_REFERENCE_LENGTH,
                    "autocomplete": "off",
                    "placeholder": "Ex. PRJ-2026-001",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_NAME_LENGTH,
                    "autocomplete": "off",
                    "placeholder": "Nom du projet",
                    "data-trim": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "maxlength": PROJECT_DESCRIPTION_LENGTH,
                    "rows": 4,
                    "placeholder": (
                        "Description générale du projet"
                    ),
                    "data-trim": True,
                }
            ),
            "contract_reference": forms.TextInput(
                attrs={
                    "maxlength": (
                        PROJECT_CONTRACT_REFERENCE_LENGTH
                    ),
                    "autocomplete": "off",
                    "placeholder": (
                        "Référence du contrat ou de la commande"
                    ),
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "comments": forms.Textarea(
                attrs={
                    "maxlength": PROJECT_COMMENT_LENGTH,
                    "rows": 4,
                    "placeholder": (
                        "Commentaires contractuels ou "
                        "administratifs"
                    ),
                    "data-trim": True,
                }
            ),
            "address_1": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_ADDRESS_LENGTH,
                    "autocomplete": "address-line1",
                    "data-trim": True,
                }
            ),
            "address_2": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_ADDRESS_LENGTH,
                    "autocomplete": "address-line2",
                    "data-trim": True,
                }
            ),
            "address_3": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_ADDRESS_LENGTH,
                    "autocomplete": "address-line3",
                    "data-trim": True,
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_POSTAL_CODE_LENGTH,
                    "autocomplete": "postal-code",
                    "inputmode": "numeric",
                    "data-trim": True,
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_CITY_LENGTH,
                    "autocomplete": "address-level2",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_COUNTRY_LENGTH,
                    "autocomplete": "country-name",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "planned_workload_hours": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": 1,
                    "inputmode": "numeric",
                }
            ),
            "contractual_start_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "contractual_end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "start_date_review": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "end_date_review": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "receipt_date_init": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "receipt_date_review": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "delivery_date_init": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "delivery_date_review": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "amount_quote_ht": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "amount_quote_ttc": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "amount_order_ht": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "amount_order_ttc": forms.NumberInput(
                attrs={
                    "min": 0,
                    "step": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "currency": forms.TextInput(
                attrs={
                    "maxlength": PROJECT_CURRENCY_LENGTH,
                    "autocomplete": "off",
                    "placeholder": "EUR",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "budget_comments": forms.Textarea(
                attrs={
                    "maxlength": PROJECT_COMMENT_LENGTH,
                    "rows": 4,
                    "placeholder": (
                        "Commentaires relatifs au devis, "
                        "à la commande ou au budget vendu"
                    ),
                    "data-trim": True,
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        active_companies = (
            Company.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self.fields["company"].queryset = active_companies
        self.fields["owner_company"].queryset = active_companies
        self.fields["designer_company"].queryset = (
            active_companies
        )

        self.fields["project_manager"].queryset = (
            User.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by(
                "last_name",
                "first_name",
            )
        )

        self._configure_catalog_field(
            field_name="status",
            catalog_code="PROJECT_STATUS",
        )
        self._configure_catalog_field(
            field_name="project_type",
            catalog_code="PROJECT_TYPE",
        )

        if not self.is_bound and not self.instance.pk:
            self._apply_catalog_default("status")
            self._apply_catalog_default("project_type")

    def _configure_catalog_field(
        self,
        *,
        field_name: str,
        catalog_code: str,
    ) -> None:
        catalog = (
            CatalogValue.objects
            .filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
            )
            .values(
                "catalog_type__is_editable",
                "catalog_type__is_incremental",
            )
            .first()
        )

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

        if catalog is None:
            field.catalog_is_editable = False
            field.catalog_is_incremental = False
            return

        field.catalog_is_editable = (
            catalog["catalog_type__is_editable"]
        )
        field.catalog_is_incremental = (
            catalog["catalog_type__is_incremental"]
        )

    def _apply_catalog_default(
        self,
        field_name: str,
    ) -> None:
        default_value = (
            self.fields[field_name]
            .queryset
            .filter(is_default=True)
            .first()
        )

        if default_value is not None:
            self.initial[field_name] = default_value.pk
            
class ProjectMembershipForm(forms.ModelForm):
    """
    Affectation d'un utilisateur à un projet.
    """

    role = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_PROJECT_ROLE",
        required=True,
        label="Rôle sur le projet",
    )

    class Meta:
        model = ProjectMembership
        fields = (
            "user",
            "role",
            "is_active",
        )

        labels = {
            "user": "Utilisateur",
            "is_active": "Actif",
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["user"].queryset = (
            User.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by(
                "last_name",
                "first_name",
            )
        )

        self.fields["role"].queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code="USER_PROJECT_ROLE",
                catalog_type__is_active=True,
                is_active=True,
            )
            .select_related("catalog_type")
            .order_by(
                "sort_order",
                "label",
            )
        )

        self.fields["role"].catalog_is_editable = False
        self.fields["role"].catalog_is_incremental = False

            
ProjectMembershipFormSet = forms.inlineformset_factory(
    Project,
    ProjectMembership,
    form=ProjectMembershipForm,
    fields=(
        "user",
        "role",
        "is_active",
    ),
    extra=1,
    can_delete=True,
)
        