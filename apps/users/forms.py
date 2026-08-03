

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from common.constants.user import (
    USER_EMAIL_LENGTH,
    USER_FIRST_NAME_LENGTH,
    USER_LAST_NAME_LENGTH,
    USER_MOBILE_LENGTH,
    USER_PHONE_LENGTH,
    USER_THEME_LENGTH,
)
from common.forms.widgets import TelInput

from .models import User
from common.forms.fields import CatalogModelChoiceField


class UserForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'un utilisateur.

    Le mot de passe n'est jamais saisi dans ce formulaire.
    Un nouvel utilisateur est créé avec un mot de passe inutilisable,
    dans l'attente de la validation de son invitation.
    """

    employment_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_EMPLOYMENT_TYPE",
        required=False,
        label="Type d'emploi",
    )

    job = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_JOB",
        required=False,
        label="Métier",
    )

    global_role = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_GLOBAL_ROLE",
        required=True,
        label="Rôle global",
    )

    access_level = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_LEVEL_ACCESS",
        required=True,
        label="Niveau d'accès",
    )
    class Meta:
        model = User

        fields = (
            "last_name",
            "first_name",
            "email",
            "phone",
            "mobile",
            "company",
            "employment_type",
            "job",
            "global_role",
            "access_level",
            "is_active",
            "theme",
        )

        labels = {
            "is_active": "Utilisateur actif",
        }

        widgets = {
            "last_name": forms.TextInput(
                attrs={
                    "maxlength": USER_LAST_NAME_LENGTH,
                    "autocomplete": "family-name",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "maxlength": USER_FIRST_NAME_LENGTH,
                    "autocomplete": "given-name",
                    "data-trim": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "maxlength": USER_EMAIL_LENGTH,
                    "autocomplete": "email",
                    "placeholder": "prenom.nom@entreprise.fr",
                    "data-lowercase": True,
                    "data-trim": True,
                }
            ),
            "phone": TelInput(
                attrs={
                    "maxlength": USER_PHONE_LENGTH,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "01 23 45 67 89",
                    "data-phone": True,
                    "data-trim": True,
                }
            ),
            "mobile": TelInput(
                attrs={
                    "maxlength": USER_MOBILE_LENGTH,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "06 12 34 56 78",
                    "data-phone": True,
                    "data-trim": True,
                }
            ),
            "theme": forms.TextInput(
                attrs={
                    "maxlength": USER_THEME_LENGTH,
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = (
            Company.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self._configure_catalog_field(
            field_name="employment_type",
            catalog_code="USER_EMPLOYMENT_TYPE",
        )
        self._configure_catalog_field(
            field_name="job",
            catalog_code="USER_JOB",
        )
        self._configure_catalog_field(
            field_name="global_role",
            catalog_code="USER_GLOBAL_ROLE",
        )
        self._configure_catalog_field(
            field_name="access_level",
            catalog_code="USER_LEVEL_ACCESS",
        )

        if not self.is_bound and not self.instance.pk:
            self._apply_catalog_default("employment_type")
            self._apply_catalog_default("job")
            self._apply_catalog_default("global_role")
            self._apply_catalog_default("access_level")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)

        if user._state.adding:
            user.set_unusable_password()

        if commit:
            user.save()
            self.save_m2m()

        return user

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