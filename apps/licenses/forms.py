

from __future__ import annotations

from django import forms

from apps.companies.models import Company
from apps.licenses.models import License
from apps.licenses.services import LicenseService
from common.constants.license import (
    LICENSE_REFERENCE_LENGTH,
)
from django.utils import timezone


class LicenseForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'une licence.

    Lors de la création, la persistance est déléguée à LicenseService.
    """

    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        required=True,
        label="Société",
    )

    class Meta:
        model = License

        fields = (
            "reference",
            "project_capacity",
            "granted_at",
            "expiration_date",
        )

        widgets = {
            "reference": forms.TextInput(
                attrs={
                    "maxlength": LICENSE_REFERENCE_LENGTH,
                    "placeholder": (
                        "Numéro de commande ou de devis"
                    ),
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
            "project_capacity": forms.NumberInput(
                attrs={
                    "min": 1,
                    "inputmode": "numeric",
                }
            ),
            "granted_at": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
            "expiration_date": forms.DateInput(
                attrs={
                    "type": "date",
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

        if self.instance._state.adding:
            self.fields["granted_at"].initial = (
                timezone.localdate()
            )
        else:
            self.fields["company"].initial = (
                self.instance.client_environment.company
            )
            self.fields["company"].disabled = True
                
    def clean(self):
        cleaned_data = super().clean()

        granted_at = cleaned_data.get("granted_at")
        expiration_date = cleaned_data.get(
            "expiration_date"
        )

        if (
            granted_at is not None
            and expiration_date is not None
            and expiration_date < granted_at
        ):
            self.add_error(
                "expiration_date",
                (
                    "La date d'expiration ne peut pas être "
                    "antérieure à la date d'attribution."
                ),
            )

        return cleaned_data

    def save(self, commit: bool = True) -> License:
        if self.instance._state.adding:
            if not commit:
                raise ValueError(
                    "La création d'une licence ne prend pas "
                    "en charge commit=False."
                )

            license_instance = (
                LicenseService.create_license(
                    company=self.cleaned_data["company"],
                    reference=self.cleaned_data["reference"],
                    granted_at=self.cleaned_data["granted_at"],
                    expiration_date=self.cleaned_data[
                        "expiration_date"
                    ],
                    project_capacity=self.cleaned_data[
                        "project_capacity"
                    ],
                )
            )

            self.instance = license_instance

            return license_instance

        license_instance = super().save(
            commit=False,
        )

        if commit:
            license_instance.full_clean()
            license_instance.save()
            self.save_m2m()

        return license_instance