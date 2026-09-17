

from django import forms

from common.constants.company import (
    COMPANY_EMAIL_LENGTH,
    COMPANY_NAME_LENGTH,
    COMPANY_PHONE_LENGTH,
    COMPANY_SIRET_LENGTH,
    COMPANY_VAT_NUMBER_LENGTH,
)
from common.forms.widgets import (
    FileUploadInput,
    TelInput,
)

from .models import Company


class CompanyForm(forms.ModelForm):
    DEFAULT_COUNTRY = "FRANCE"

    class Meta:
        model = Company

        fields = (
            "name",
            "logo",
            "siret",
            "vat_number",
            "email",
            "phone",
            "address_1",
            "address_2",
            "address_3",
            "postal_code",
            "city",
            "country",
            "is_active",
        )

        labels = {
            "is_active": "Société active",
        }

        help_texts = {
            "name": "Nom utilisé dans l'application.",
        }

        widgets = {
            "logo": FileUploadInput(),
            "name": forms.TextInput(
                attrs={
                    "maxlength": COMPANY_NAME_LENGTH,
                    "placeholder": (
                        "Nom utilisé dans l'application"
                    ),
                    "autocomplete": "organization",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "maxlength": COMPANY_EMAIL_LENGTH,
                    "autocomplete": "email",
                    "placeholder": (
                        "contact@entreprise.fr"
                    ),
                    "data-lowercase": True,
                    "data-trim": True,
                }
            ),
            "phone": TelInput(
                attrs={
                    "maxlength": COMPANY_PHONE_LENGTH,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "01 23 45 67 89",
                    "data-phone": True,
                    "data-trim": True,
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "autocomplete": "postal-code",
                    "inputmode": "numeric",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "autocomplete": "address-level2",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "autocomplete": "country-name",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "siret": forms.TextInput(
                attrs={
                    # 14 chiffres + 3 espaces de présentation.
                    "maxlength": (
                        COMPANY_SIRET_LENGTH + 3
                    ),
                    "placeholder": "123 456 789 00012",
                    "autocomplete": "off",
                    "inputmode": "numeric",
                    "data-siret": True,
                    "data-trim": True,
                }
            ),
            "vat_number": forms.TextInput(
                attrs={
                    "maxlength": COMPANY_VAT_NUMBER_LENGTH,
                    "placeholder": "Ex. FR12345678901",
                    "autocomplete": "off",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )

        if (
            not self.is_bound
            and self.instance._state.adding
        ):
            self.initial["country"] = (
                self.DEFAULT_COUNTRY
            )

        if (
            not self.is_bound
            and self.instance.siret
        ):
            self.initial["siret"] = (
                self.format_siret(
                    self.instance.siret
                )
            )

    def clean_siret(self) -> str:
        """
        La base conserve le SIRET normalisé, sans espaces.
        """
        siret = self.cleaned_data.get(
            "siret",
            "",
        )

        return "".join(siret.split())

    @staticmethod
    def format_siret(value: str) -> str:
        digits = "".join(
            character
            for character in value
            if character.isdigit()
        )[:COMPANY_SIRET_LENGTH]

        groups = (
            digits[:3],
            digits[3:6],
            digits[6:9],
            digits[9:14],
        )

        return " ".join(
            group
            for group in groups
            if group
        )